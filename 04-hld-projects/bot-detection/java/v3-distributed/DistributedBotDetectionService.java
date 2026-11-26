package v3;

import java.util.*;
import java.util.concurrent.*;

public class DistributedBotDetectionService {

    public interface FeatureService {
        FeatureResult getFeatures(String accountId);
    }

    public static class FeatureResult {
        public final Map<String, Double> features;
        public final boolean isDelayed;

        public FeatureResult(Map<String, Double> features, boolean isDelayed) {
            this.features = features;
            this.isDelayed = isDelayed;
        }
    }

    public interface RulesEngine {
        RuleResult evaluate(String accountId, Map<String, Double> features);
    }

    public static class RuleResult {
        public final double score;
        public final boolean matchedHighPrecision;

        public RuleResult(double score, boolean matchedHighPrecision) {
            this.score = score;
            this.matchedHighPrecision = matchedHighPrecision;
        }
    }

    public interface ModelService {
        ModelResult evaluate(String accountId, Map<String, Double> features);
    }

    public static class ModelResult {
        public final double score;
        public final boolean timedOut;

        public ModelResult(double score, boolean timedOut) {
            this.score = score;
            this.timedOut = timedOut;
        }
    }

    public interface AnomalyDetector {
        double getAnomalyScore(String accountId, Map<String, Double> features);
    }

    public interface PolicyEngine {
        PolicyDecision decideAction(double riskScore, double confidence);
        String getPolicyVersion();
    }

    public static class PolicyDecision {
        public final ActionType action;
        public final String reason;

        public PolicyDecision(ActionType action, String reason) {
            this.action = action;
            this.reason = reason;
        }
    }

    public enum ActionType {
        ALLOW, CHALLENGE, LIMIT, SUSPEND, ROUTE_TO_REVIEW
    }

    public interface DeferredAnalysisService {
        void enqueueForAnalysis(String accountId, Map<String, Double> features);
    }

    public interface LabelStore {
        void saveLabel(String accountId, String label, double agreement, boolean holdback);
    }

    public interface MetricsService {
        void increment(String metricName);
        void recordValue(String metricName, double value);
    }

    public interface ActionStore {
        void saveAction(String accountId, ActionEvent event, String idempotencyKey);
    }

    public static class ActionEvent {
        public final ActionType action;
        public final String reason;
        public final String policyVersion;
        public final String rollbackRef;

        public ActionEvent(ActionType action, String reason, String policyVersion, String rollbackRef) {
            this.action = action;
            this.reason = reason;
            this.policyVersion = policyVersion;
            this.rollbackRef = rollbackRef;
        }
    }

    // NEW FOR V3
    public interface ConsensusNode {
        boolean proposeRiskState(String accountId, double score, double confidence, ActionType action);
    }

    public interface ConsistentHashRouter {
        String getRoute(String accountId);
    }

    public static class CircuitBreaker {
        private int failureCount = 0;
        private final int threshold;
        private long lastFailureTime = 0;
        private final long resetTimeoutMs;
        private boolean open = false;

        public CircuitBreaker(int threshold, long resetTimeoutMs) {
            this.threshold = threshold;
            this.resetTimeoutMs = resetTimeoutMs;
        }

        public synchronized boolean allowRequest() {
            if (open) {
                if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                    open = false;
                    failureCount = 0;
                    return true;
                }
                return false;
            }
            return true;
        }

        public synchronized void recordSuccess() {
            if (open) return; // Should not happen, but just in case
            failureCount = 0;
        }

        public synchronized void recordFailure() {
            failureCount++;
            lastFailureTime = System.currentTimeMillis();
            if (failureCount >= threshold) {
                open = true;
            }
        }

        public synchronized boolean isOpen() {
            return open;
        }
    }

    private final FeatureService featureService;
    private final RulesEngine rulesEngine;
    private final ModelService modelService;
    private final AnomalyDetector anomalyDetector;
    private final PolicyEngine policyEngine;
    private final DeferredAnalysisService deferredAnalysisService;
    private final LabelStore labelStore;
    private final MetricsService metricsService;
    private final ActionStore actionStore;

    // V3 specific
    private final ConsistentHashRouter router;
    private final List<ConsensusNode> consensusNodes;
    private final CircuitBreaker clusterCircuitBreaker;

    private static final double AGREEMENT_THRESHOLD = 0.8;

    // Fallback cluster settings
    private boolean clusterDegraded = false;

    public DistributedBotDetectionService(
            FeatureService featureService,
            RulesEngine rulesEngine,
            ModelService modelService,
            AnomalyDetector anomalyDetector,
            PolicyEngine policyEngine,
            DeferredAnalysisService deferredAnalysisService,
            LabelStore labelStore,
            MetricsService metricsService,
            ActionStore actionStore,
            ConsistentHashRouter router,
            List<ConsensusNode> consensusNodes,
            CircuitBreaker clusterCircuitBreaker) {
        this.featureService = featureService;
        this.rulesEngine = rulesEngine;
        this.modelService = modelService;
        this.anomalyDetector = anomalyDetector;
        this.policyEngine = policyEngine;
        this.deferredAnalysisService = deferredAnalysisService;
        this.labelStore = labelStore;
        this.metricsService = metricsService;
        this.actionStore = actionStore;
        this.router = router;
        this.consensusNodes = consensusNodes;
        this.clusterCircuitBreaker = clusterCircuitBreaker;
    }

    public EvaluationResult evaluateAccount(String accountId, String eventId) {
        long startTime = System.currentTimeMillis();

        String routeId = router.getRoute(accountId);
        metricsService.increment("route." + routeId);

        if (!clusterCircuitBreaker.allowRequest()) {
            this.clusterDegraded = true;
            metricsService.increment("cluster.degraded");
        } else {
            this.clusterDegraded = false;
        }

        FeatureResult featureResult = featureService.getFeatures(accountId);
        double confidence = 1.0;

        if (featureResult.isDelayed) {
            confidence -= 0.3; // Lower confidence on delayed/fallback features
            metricsService.increment("features.delayed");
        }

        RuleResult ruleResult = rulesEngine.evaluate(accountId, featureResult.features);

        double finalScore = 0.0;

        if (clusterDegraded) {
             // Circuit breaker fallback to high-precision deterministic rules during cluster degradation
             finalScore = ruleResult.matchedHighPrecision ? 0.9 : 0.0; // very conservative
             confidence -= 0.5;
             metricsService.increment("eval.fallback.rules_only");
        } else {
            ModelResult modelResult = modelService.evaluate(accountId, featureResult.features);
            if (modelResult.timedOut) {
                clusterCircuitBreaker.recordFailure();
                metricsService.increment("model.timeout.degraded_mode");
                confidence -= 0.4;
                // In degraded mode, rely on high precision rules
                finalScore = ruleResult.matchedHighPrecision ? 0.9 : ruleResult.score;
                deferredAnalysisService.enqueueForAnalysis(accountId, featureResult.features);
            } else {
                clusterCircuitBreaker.recordSuccess();
                double anomalyScore = anomalyDetector.getAnomalyScore(accountId, featureResult.features);
                // Combine scores (simplified ensemble logic)
                finalScore = (ruleResult.score * 0.3) + (modelResult.score * 0.5) + (anomalyScore * 0.2);
                if (ruleResult.matchedHighPrecision) {
                    finalScore = Math.max(finalScore, 0.9);
                }
            }
        }

        PolicyDecision decision = policyEngine.decideAction(finalScore, confidence);

        // Sync across regions using distributed consensus
        int acks = 0;
        for (ConsensusNode node : consensusNodes) {
            try {
                if (node.proposeRiskState(accountId, finalScore, confidence, decision.action)) {
                    acks++;
                }
            } catch (Exception e) {
                // Ignore node failure
            }
        }

        if (acks < (consensusNodes.size() / 2) + 1) {
            metricsService.increment("consensus.failed");
            // Could adjust confidence down if state isn't synced
            confidence -= 0.1;
        }

        String rollbackRef = UUID.randomUUID().toString();
        // Use eventId as idempotency key
        String idempotencyKey = eventId;

        ActionEvent actionEvent = new ActionEvent(decision.action, decision.reason, policyEngine.getPolicyVersion(), rollbackRef);
        actionStore.saveAction(accountId, actionEvent, idempotencyKey);

        if (decision.action == ActionType.ROUTE_TO_REVIEW || decision.action == ActionType.CHALLENGE || confidence < 0.8) {
            deferredAnalysisService.enqueueForAnalysis(accountId, featureResult.features);
        }

        metricsService.recordValue("evaluation.latency.ms", (double)(System.currentTimeMillis() - startTime));

        return new EvaluationResult(finalScore, confidence, decision.action, rollbackRef, routeId);
    }

    public void submitInvestigatorLabel(String accountId, String label, double agreementScore) {
        boolean holdback = agreementScore < AGREEMENT_THRESHOLD;
        if (holdback) {
            metricsService.increment("label.held_back");
        } else {
            metricsService.increment("label.accepted");
        }
        labelStore.saveLabel(accountId, label, agreementScore, holdback);
    }

    public static class EvaluationResult {
        public final double score;
        public final double confidence;
        public final ActionType action;
        public final String rollbackRef;
        public final String routeId;

        public EvaluationResult(double score, double confidence, ActionType action, String rollbackRef, String routeId) {
            this.score = score;
            this.confidence = confidence;
            this.action = action;
            this.rollbackRef = rollbackRef;
            this.routeId = routeId;
        }
    }
}
