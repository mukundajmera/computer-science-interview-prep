import java.util.*;

public class ScaledBotDetectionService {

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
        void saveAction(String accountId, ActionEvent event);
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

    private final FeatureService featureService;
    private final RulesEngine rulesEngine;
    private final ModelService modelService;
    private final AnomalyDetector anomalyDetector;
    private final PolicyEngine policyEngine;
    private final DeferredAnalysisService deferredAnalysisService;
    private final LabelStore labelStore;
    private final MetricsService metricsService;
    private final ActionStore actionStore;

    private static final double AGREEMENT_THRESHOLD = 0.8;

    public ScaledBotDetectionService(
            FeatureService featureService,
            RulesEngine rulesEngine,
            ModelService modelService,
            AnomalyDetector anomalyDetector,
            PolicyEngine policyEngine,
            DeferredAnalysisService deferredAnalysisService,
            LabelStore labelStore,
            MetricsService metricsService,
            ActionStore actionStore) {
        this.featureService = featureService;
        this.rulesEngine = rulesEngine;
        this.modelService = modelService;
        this.anomalyDetector = anomalyDetector;
        this.policyEngine = policyEngine;
        this.deferredAnalysisService = deferredAnalysisService;
        this.labelStore = labelStore;
        this.metricsService = metricsService;
        this.actionStore = actionStore;
    }

    public EvaluationResult evaluateAccount(String accountId) {
        long startTime = System.currentTimeMillis();

        FeatureResult featureResult = featureService.getFeatures(accountId);
        double confidence = 1.0;

        if (featureResult.isDelayed) {
            confidence -= 0.3; // Lower confidence on delayed/fallback features
            metricsService.increment("features.delayed");
        }

        RuleResult ruleResult = rulesEngine.evaluate(accountId, featureResult.features);

        ModelResult modelResult = modelService.evaluate(accountId, featureResult.features);

        double finalScore = 0.0;
        if (modelResult.timedOut) {
            metricsService.increment("model.timeout.degraded_mode");
            confidence -= 0.4;
            // In degraded mode, rely on high precision rules
            finalScore = ruleResult.matchedHighPrecision ? 0.9 : ruleResult.score;
            deferredAnalysisService.enqueueForAnalysis(accountId, featureResult.features);
        } else {
            double anomalyScore = anomalyDetector.getAnomalyScore(accountId, featureResult.features);
            // Combine scores (simplified ensemble logic)
            finalScore = (ruleResult.score * 0.3) + (modelResult.score * 0.5) + (anomalyScore * 0.2);
            if (ruleResult.matchedHighPrecision) {
                finalScore = Math.max(finalScore, 0.9);
            }
        }

        PolicyDecision decision = policyEngine.decideAction(finalScore, confidence);

        String rollbackRef = UUID.randomUUID().toString();
        ActionEvent actionEvent = new ActionEvent(decision.action, decision.reason, policyEngine.getPolicyVersion(), rollbackRef);
        actionStore.saveAction(accountId, actionEvent);

        if (decision.action == ActionType.ROUTE_TO_REVIEW || decision.action == ActionType.CHALLENGE || confidence < 0.8) {
            deferredAnalysisService.enqueueForAnalysis(accountId, featureResult.features);
        }

        metricsService.recordValue("evaluation.latency.ms", (double)(System.currentTimeMillis() - startTime));

        return new EvaluationResult(finalScore, confidence, decision.action, rollbackRef);
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

        public EvaluationResult(double score, double confidence, ActionType action, String rollbackRef) {
            this.score = score;
            this.confidence = confidence;
            this.action = action;
            this.rollbackRef = rollbackRef;
        }
    }
}
