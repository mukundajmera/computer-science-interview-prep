import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

class ScaledBotDetectionServiceV2Test {

    private InMemoryFeatureService featureService;
    private InMemoryRulesEngine rulesEngine;
    private InMemoryModelService modelService;
    private InMemoryAnomalyDetector anomalyDetector;
    private InMemoryPolicyEngine policyEngine;
    private InMemoryDeferredAnalysisService deferredAnalysisService;
    private InMemoryLabelStore labelStore;
    private InMemoryMetricsService metricsService;
    private InMemoryActionStore actionStore;
    private ScaledBotDetectionService service;

    @BeforeEach
    void setUp() {
        featureService = new InMemoryFeatureService();
        rulesEngine = new InMemoryRulesEngine();
        modelService = new InMemoryModelService();
        anomalyDetector = new InMemoryAnomalyDetector();
        policyEngine = new InMemoryPolicyEngine();
        deferredAnalysisService = new InMemoryDeferredAnalysisService();
        labelStore = new InMemoryLabelStore();
        metricsService = new InMemoryMetricsService();
        actionStore = new InMemoryActionStore();

        service = new ScaledBotDetectionService(
            featureService, rulesEngine, modelService, anomalyDetector,
            policyEngine, deferredAnalysisService, labelStore, metricsService, actionStore
        );
    }

    @Test
    void testHealthyScoringPath() {
        featureService.setFeatures(new ScaledBotDetectionService.FeatureResult(Map.of("login_velocity", 0.1), false));
        rulesEngine.setResult(new ScaledBotDetectionService.RuleResult(0.1, false));
        modelService.setResult(new ScaledBotDetectionService.ModelResult(0.2, false));
        anomalyDetector.setScore(0.1);

        // score = 0.1*0.3 + 0.2*0.5 + 0.1*0.2 = 0.03 + 0.1 + 0.02 = 0.15
        policyEngine.setDecision(new ScaledBotDetectionService.PolicyDecision(ScaledBotDetectionService.ActionType.ALLOW, "clean"));

        ScaledBotDetectionService.EvaluationResult result = service.evaluateAccount("user1");

        assertEquals(1.0, result.confidence, "Confidence should be 1.0 for healthy features");
        assertEquals(ScaledBotDetectionService.ActionType.ALLOW, result.action);

        ScaledBotDetectionService.ActionEvent savedAction = actionStore.getLastAction("user1");
        assertNotNull(savedAction);
        assertEquals("v2", savedAction.policyVersion);
        assertNotNull(savedAction.rollbackRef);
    }

    @Test
    void testDelayedFeaturesFallbackAndRouteToChallenge() {
        featureService.setFeatures(new ScaledBotDetectionService.FeatureResult(Map.of("login_velocity", 0.5), true));
        rulesEngine.setResult(new ScaledBotDetectionService.RuleResult(0.5, false));
        modelService.setResult(new ScaledBotDetectionService.ModelResult(0.5, false));
        anomalyDetector.setScore(0.5);

        policyEngine.setDecision(new ScaledBotDetectionService.PolicyDecision(ScaledBotDetectionService.ActionType.CHALLENGE, "uncertain"));

        ScaledBotDetectionService.EvaluationResult result = service.evaluateAccount("user2");

        assertTrue(result.confidence < 1.0, "Confidence should be lowered for delayed features");
        assertEquals(ScaledBotDetectionService.ActionType.CHALLENGE, result.action);
        assertTrue(deferredAnalysisService.wasEnqueued("user2"), "Should be routed to deferred analysis due to lower confidence");
        assertEquals(1, metricsService.getCount("features.delayed"));
    }

    @Test
    void testModelTimeoutDegradedMode() {
        featureService.setFeatures(new ScaledBotDetectionService.FeatureResult(Map.of("login_velocity", 0.9), false));
        rulesEngine.setResult(new ScaledBotDetectionService.RuleResult(0.9, true)); // matched high precision
        modelService.setResult(new ScaledBotDetectionService.ModelResult(0.0, true)); // timeout
        anomalyDetector.setScore(0.0);

        policyEngine.setDecision(new ScaledBotDetectionService.PolicyDecision(ScaledBotDetectionService.ActionType.SUSPEND, "rules_only"));

        ScaledBotDetectionService.EvaluationResult result = service.evaluateAccount("user3");

        assertTrue(result.confidence < 1.0, "Confidence should be lowered for model timeout");
        assertEquals(ScaledBotDetectionService.ActionType.SUSPEND, result.action);
        assertEquals(1, metricsService.getCount("model.timeout.degraded_mode"));
        assertTrue(deferredAnalysisService.wasEnqueued("user3"), "Degraded mode should trigger deferred analysis");
    }

    @Test
    void testLowAgreementLabelHoldback() {
        service.submitInvestigatorLabel("user4", "BOT", 0.7); // Below 0.8

        assertEquals(1, metricsService.getCount("label.held_back"));
        assertEquals(0, metricsService.getCount("label.accepted"));
        assertTrue(labelStore.wasHeldBack("user4"));
    }

    @Test
    void testHighAgreementLabelAccepted() {
        service.submitInvestigatorLabel("user5", "BOT", 0.9); // Above 0.8

        assertEquals(0, metricsService.getCount("label.held_back"));
        assertEquals(1, metricsService.getCount("label.accepted"));
        assertFalse(labelStore.wasHeldBack("user5"));
    }

    // Fakes
    static class InMemoryFeatureService implements ScaledBotDetectionService.FeatureService {
        private ScaledBotDetectionService.FeatureResult result = new ScaledBotDetectionService.FeatureResult(new HashMap<>(), false);
        void setFeatures(ScaledBotDetectionService.FeatureResult result) { this.result = result; }
        @Override public ScaledBotDetectionService.FeatureResult getFeatures(String accountId) { return result; }
    }

    static class InMemoryRulesEngine implements ScaledBotDetectionService.RulesEngine {
        private ScaledBotDetectionService.RuleResult result = new ScaledBotDetectionService.RuleResult(0.0, false);
        void setResult(ScaledBotDetectionService.RuleResult result) { this.result = result; }
        @Override public ScaledBotDetectionService.RuleResult evaluate(String accountId, Map<String, Double> features) { return result; }
    }

    static class InMemoryModelService implements ScaledBotDetectionService.ModelService {
        private ScaledBotDetectionService.ModelResult result = new ScaledBotDetectionService.ModelResult(0.0, false);
        void setResult(ScaledBotDetectionService.ModelResult result) { this.result = result; }
        @Override public ScaledBotDetectionService.ModelResult evaluate(String accountId, Map<String, Double> features) { return result; }
    }

    static class InMemoryAnomalyDetector implements ScaledBotDetectionService.AnomalyDetector {
        private double score = 0.0;
        void setScore(double score) { this.score = score; }
        @Override public double getAnomalyScore(String accountId, Map<String, Double> features) { return score; }
    }

    static class InMemoryPolicyEngine implements ScaledBotDetectionService.PolicyEngine {
        private ScaledBotDetectionService.PolicyDecision decision = new ScaledBotDetectionService.PolicyDecision(ScaledBotDetectionService.ActionType.ALLOW, "clean");
        void setDecision(ScaledBotDetectionService.PolicyDecision decision) { this.decision = decision; }
        @Override public ScaledBotDetectionService.PolicyDecision decideAction(double riskScore, double confidence) { return decision; }
        @Override public String getPolicyVersion() { return "v2"; }
    }

    static class InMemoryDeferredAnalysisService implements ScaledBotDetectionService.DeferredAnalysisService {
        private Set<String> enqueued = new HashSet<>();
        @Override public void enqueueForAnalysis(String accountId, Map<String, Double> features) { enqueued.add(accountId); }
        boolean wasEnqueued(String accountId) { return enqueued.contains(accountId); }
    }

    static class InMemoryLabelStore implements ScaledBotDetectionService.LabelStore {
        private Map<String, Boolean> heldBack = new HashMap<>();
        @Override public void saveLabel(String accountId, String label, double agreement, boolean holdback) {
            heldBack.put(accountId, holdback);
        }
        boolean wasHeldBack(String accountId) { return heldBack.getOrDefault(accountId, false); }
    }

    static class InMemoryMetricsService implements ScaledBotDetectionService.MetricsService {
        private Map<String, Integer> counts = new HashMap<>();
        @Override public void increment(String metricName) { counts.put(metricName, counts.getOrDefault(metricName, 0) + 1); }
        @Override public void recordValue(String metricName, double value) {}
        int getCount(String metricName) { return counts.getOrDefault(metricName, 0); }
    }

    static class InMemoryActionStore implements ScaledBotDetectionService.ActionStore {
        private Map<String, ScaledBotDetectionService.ActionEvent> actions = new HashMap<>();
        @Override public void saveAction(String accountId, ScaledBotDetectionService.ActionEvent event) {
            actions.put(accountId, event);
        }
        ScaledBotDetectionService.ActionEvent getLastAction(String accountId) { return actions.get(accountId); }
    }
}
