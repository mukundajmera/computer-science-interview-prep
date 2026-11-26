package v3;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedBotDetectionServiceTest {

    private DistributedBotDetectionService service;
    private DummyFeatureService featureService;
    private DummyRulesEngine rulesEngine;
    private DummyModelService modelService;
    private DummyAnomalyDetector anomalyDetector;
    private DummyPolicyEngine policyEngine;
    private DummyDeferredAnalysisService deferredAnalysisService;
    private DummyLabelStore labelStore;
    private DummyMetricsService metricsService;
    private DummyActionStore actionStore;
    private DummyConsistentHashRouter router;
    private List<DistributedBotDetectionService.ConsensusNode> consensusNodes;
    private DistributedBotDetectionService.CircuitBreaker circuitBreaker;

    @BeforeEach
    public void setUp() {
        featureService = new DummyFeatureService();
        rulesEngine = new DummyRulesEngine();
        modelService = new DummyModelService();
        anomalyDetector = new DummyAnomalyDetector();
        policyEngine = new DummyPolicyEngine();
        deferredAnalysisService = new DummyDeferredAnalysisService();
        labelStore = new DummyLabelStore();
        metricsService = new DummyMetricsService();
        actionStore = new DummyActionStore();
        router = new DummyConsistentHashRouter();
        consensusNodes = Arrays.asList(new DummyConsensusNode(true), new DummyConsensusNode(true), new DummyConsensusNode(true));
        circuitBreaker = new DistributedBotDetectionService.CircuitBreaker(2, 1000);

        service = new DistributedBotDetectionService(
                featureService, rulesEngine, modelService, anomalyDetector, policyEngine,
                deferredAnalysisService, labelStore, metricsService, actionStore,
                router, consensusNodes, circuitBreaker
        );
    }

    @Test
    public void testNormalEvaluation() {
        DistributedBotDetectionService.EvaluationResult result = service.evaluateAccount("user123", "event-1");

        assertNotNull(result);
        assertEquals(DistributedBotDetectionService.ActionType.ALLOW, result.action);
        assertEquals("shard-user123", result.routeId);
        assertNotNull(result.rollbackRef);

        // Ensure action was stored with idempotency key
        assertTrue(actionStore.lastSavedIdempotencyKey != null && actionStore.lastSavedIdempotencyKey.equals("event-1"));
    }

    @Test
    public void testModelTimeoutDegradedMode() {
        modelService.shouldTimeout = true;

        DistributedBotDetectionService.EvaluationResult result = service.evaluateAccount("user456", "event-2");

        assertNotNull(result);
        // Confidence should be lower
        assertTrue(result.confidence < 1.0);
        // Action could be ALLOW based on our dummy, but rules handle score

        // Failure count in circuit breaker should increase
        assertEquals(1, metricsService.getMetric("model.timeout.degraded_mode"));

        // Ensure deferred analysis was triggered
        assertTrue(deferredAnalysisService.enqueued);
    }

    @Test
    public void testCircuitBreakerFallbackRules() {
        // Force circuit breaker to open
        circuitBreaker.recordFailure();
        circuitBreaker.recordFailure();
        assertTrue(circuitBreaker.isOpen());

        rulesEngine.matchedHighPrecision = true;

        DistributedBotDetectionService.EvaluationResult result = service.evaluateAccount("user789", "event-3");

        // Score should be 0.9 due to fallback high-precision match
        assertEquals(0.9, result.score, 0.01);
        assertEquals(1, metricsService.getMetric("cluster.degraded"));
        assertEquals(1, metricsService.getMetric("eval.fallback.rules_only"));
    }

    @Test
    public void testConsensusFailureReducesConfidence() {
        // Change consensus nodes to all fail
        consensusNodes = Arrays.asList(new DummyConsensusNode(false), new DummyConsensusNode(false), new DummyConsensusNode(false));
        service = new DistributedBotDetectionService(
                featureService, rulesEngine, modelService, anomalyDetector, policyEngine,
                deferredAnalysisService, labelStore, metricsService, actionStore,
                router, consensusNodes, circuitBreaker
        );

        DistributedBotDetectionService.EvaluationResult result = service.evaluateAccount("user999", "event-4");

        // Normal confidence is 1.0, consensus failure drops it by 0.1
        assertEquals(0.9, result.confidence, 0.01);
        assertEquals(1, metricsService.getMetric("consensus.failed"));
    }

    // Dummy Implementations
    private static class DummyFeatureService implements DistributedBotDetectionService.FeatureService {
        boolean delayed = false;
        @Override
        public DistributedBotDetectionService.FeatureResult getFeatures(String accountId) {
            return new DistributedBotDetectionService.FeatureResult(new HashMap<>(), delayed);
        }
    }

    private static class DummyRulesEngine implements DistributedBotDetectionService.RulesEngine {
        double score = 0.1;
        boolean matchedHighPrecision = false;
        @Override
        public DistributedBotDetectionService.RuleResult evaluate(String accountId, Map<String, Double> features) {
            return new DistributedBotDetectionService.RuleResult(score, matchedHighPrecision);
        }
    }

    private static class DummyModelService implements DistributedBotDetectionService.ModelService {
        double score = 0.2;
        boolean shouldTimeout = false;
        @Override
        public DistributedBotDetectionService.ModelResult evaluate(String accountId, Map<String, Double> features) {
            return new DistributedBotDetectionService.ModelResult(score, shouldTimeout);
        }
    }

    private static class DummyAnomalyDetector implements DistributedBotDetectionService.AnomalyDetector {
        double score = 0.05;
        @Override
        public double getAnomalyScore(String accountId, Map<String, Double> features) {
            return score;
        }
    }

    private static class DummyPolicyEngine implements DistributedBotDetectionService.PolicyEngine {
        @Override
        public DistributedBotDetectionService.PolicyDecision decideAction(double riskScore, double confidence) {
            return new DistributedBotDetectionService.PolicyDecision(DistributedBotDetectionService.ActionType.ALLOW, "looks fine");
        }
        @Override
        public String getPolicyVersion() {
            return "1.0";
        }
    }

    private static class DummyDeferredAnalysisService implements DistributedBotDetectionService.DeferredAnalysisService {
        boolean enqueued = false;
        @Override
        public void enqueueForAnalysis(String accountId, Map<String, Double> features) {
            enqueued = true;
        }
    }

    private static class DummyLabelStore implements DistributedBotDetectionService.LabelStore {
        @Override
        public void saveLabel(String accountId, String label, double agreement, boolean holdback) {
        }
    }

    private static class DummyMetricsService implements DistributedBotDetectionService.MetricsService {
        Map<String, Integer> counts = new HashMap<>();
        @Override
        public void increment(String metricName) {
            counts.put(metricName, counts.getOrDefault(metricName, 0) + 1);
        }
        @Override
        public void recordValue(String metricName, double value) {
        }
        public int getMetric(String name) {
            return counts.getOrDefault(name, 0);
        }
    }

    private static class DummyActionStore implements DistributedBotDetectionService.ActionStore {
        String lastSavedIdempotencyKey = null;
        @Override
        public void saveAction(String accountId, DistributedBotDetectionService.ActionEvent event, String idempotencyKey) {
            lastSavedIdempotencyKey = idempotencyKey;
        }
    }

    private static class DummyConsistentHashRouter implements DistributedBotDetectionService.ConsistentHashRouter {
        @Override
        public String getRoute(String accountId) {
            return "shard-" + accountId;
        }
    }

    private static class DummyConsensusNode implements DistributedBotDetectionService.ConsensusNode {
        boolean willSucceed;
        public DummyConsensusNode(boolean willSucceed) {
            this.willSucceed = willSucceed;
        }
        @Override
        public boolean proposeRiskState(String accountId, double score, double confidence, DistributedBotDetectionService.ActionType action) {
            return willSucceed;
        }
    }
}
