import pytest
import os
import sys

# dynamic sys.path import to avoid ImportErrors with hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))
from distributed_bot_detection_service import (
    DistributedBotDetectionService, ActionType, FeatureResult, RuleResult, ModelResult,
    PolicyDecision, ActionEvent, CircuitBreaker
)

class DummyFeatureService:
    def __init__(self, delayed=False):
        self.delayed = delayed

    def get_features(self, account_id):
        return FeatureResult(features={}, is_delayed=self.delayed)

class DummyRulesEngine:
    def __init__(self, score=0.1, matched=False):
        self.score = score
        self.matched = matched

    def evaluate(self, account_id, features):
        return RuleResult(score=self.score, matched_high_precision=self.matched)

class DummyModelService:
    def __init__(self, score=0.2, timeout=False):
        self.score = score
        self.timeout = timeout

    def evaluate(self, account_id, features):
        return ModelResult(score=self.score, timed_out=self.timeout)

class DummyAnomalyDetector:
    def get_anomaly_score(self, account_id, features):
        return 0.05

class DummyPolicyEngine:
    def decide_action(self, risk_score, confidence):
        return PolicyDecision(action=ActionType.ALLOW, reason="looks fine")

    def get_policy_version(self):
        return "1.0"

class DummyDeferredAnalysisService:
    def __init__(self):
        self.enqueued = False

    def enqueue_for_analysis(self, account_id, features):
        self.enqueued = True

class DummyLabelStore:
    def save_label(self, account_id, label, agreement, holdback):
        pass

class DummyMetricsService:
    def __init__(self):
        self.counts = {}

    def increment(self, metric_name):
        self.counts[metric_name] = self.counts.get(metric_name, 0) + 1

    def record_value(self, metric_name, value):
        pass

    def get_metric(self, name):
        return self.counts.get(name, 0)

class DummyActionStore:
    def __init__(self):
        self.last_saved_idempotency_key = None

    def save_action(self, account_id, event, idempotency_key):
        self.last_saved_idempotency_key = idempotency_key

class DummyConsistentHashRouter:
    def get_route(self, account_id):
        return f"shard-{account_id}"

class DummyConsensusNode:
    def __init__(self, will_succeed):
        self.will_succeed = will_succeed

    def propose_risk_state(self, account_id, score, confidence, action):
        return self.will_succeed

@pytest.fixture
def base_service():
    return DistributedBotDetectionService(
        feature_service=DummyFeatureService(),
        rules_engine=DummyRulesEngine(),
        model_service=DummyModelService(),
        anomaly_detector=DummyAnomalyDetector(),
        policy_engine=DummyPolicyEngine(),
        deferred_analysis_service=DummyDeferredAnalysisService(),
        label_store=DummyLabelStore(),
        metrics_service=DummyMetricsService(),
        action_store=DummyActionStore(),
        router=DummyConsistentHashRouter(),
        consensus_nodes=[DummyConsensusNode(True), DummyConsensusNode(True), DummyConsensusNode(True)],
        cluster_circuit_breaker=CircuitBreaker(threshold=2, reset_timeout_ms=1000)
    )

def test_normal_evaluation(base_service):
    result = base_service.evaluate_account("user123", "event-1")

    assert result is not None
    assert result.action == ActionType.ALLOW
    assert result.route_id == "shard-user123"
    assert result.rollback_ref is not None
    assert base_service.action_store.last_saved_idempotency_key == "event-1"

def test_model_timeout_degraded_mode(base_service):
    base_service.model_service.timeout = True

    result = base_service.evaluate_account("user456", "event-2")

    assert result is not None
    assert result.confidence < 1.0
    assert base_service.metrics_service.get_metric("model.timeout.degraded_mode") == 1
    assert base_service.deferred_analysis_service.enqueued

def test_circuit_breaker_fallback_rules(base_service):
    # Force circuit breaker to open
    base_service.cluster_circuit_breaker.record_failure()
    base_service.cluster_circuit_breaker.record_failure()
    assert base_service.cluster_circuit_breaker.is_open()

    base_service.rules_engine.matched = True

    result = base_service.evaluate_account("user789", "event-3")

    assert result.score == 0.9
    assert base_service.metrics_service.get_metric("cluster.degraded") == 1
    assert base_service.metrics_service.get_metric("eval.fallback.rules_only") == 1

def test_consensus_failure_reduces_confidence():
    service = DistributedBotDetectionService(
        feature_service=DummyFeatureService(),
        rules_engine=DummyRulesEngine(),
        model_service=DummyModelService(),
        anomaly_detector=DummyAnomalyDetector(),
        policy_engine=DummyPolicyEngine(),
        deferred_analysis_service=DummyDeferredAnalysisService(),
        label_store=DummyLabelStore(),
        metrics_service=DummyMetricsService(),
        action_store=DummyActionStore(),
        router=DummyConsistentHashRouter(),
        consensus_nodes=[DummyConsensusNode(False), DummyConsensusNode(False), DummyConsensusNode(False)],
        cluster_circuit_breaker=CircuitBreaker(threshold=2, reset_timeout_ms=1000)
    )

    result = service.evaluate_account("user999", "event-4")

    # Confidence drops from 1.0 to 0.9 due to consensus failure
    assert abs(result.confidence - 0.9) < 0.01
    assert service.metrics_service.get_metric("consensus.failed") == 1
