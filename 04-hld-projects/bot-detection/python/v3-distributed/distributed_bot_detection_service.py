from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import uuid
import time
import logging

class ActionType(Enum):
    ALLOW = "ALLOW"
    CHALLENGE = "CHALLENGE"
    LIMIT = "LIMIT"
    SUSPEND = "SUSPEND"
    ROUTE_TO_REVIEW = "ROUTE_TO_REVIEW"

@dataclass
class FeatureResult:
    features: Dict[str, float]
    is_delayed: bool

class FeatureService:
    def get_features(self, account_id: str) -> FeatureResult:
        pass

@dataclass
class RuleResult:
    score: float
    matched_high_precision: bool

class RulesEngine:
    def evaluate(self, account_id: str, features: Dict[str, float]) -> RuleResult:
        pass

@dataclass
class ModelResult:
    score: float
    timed_out: bool

class ModelService:
    def evaluate(self, account_id: str, features: Dict[str, float]) -> ModelResult:
        pass

class AnomalyDetector:
    def get_anomaly_score(self, account_id: str, features: Dict[str, float]) -> float:
        pass

@dataclass
class PolicyDecision:
    action: ActionType
    reason: str

class PolicyEngine:
    def decide_action(self, risk_score: float, confidence: float) -> PolicyDecision:
        pass

    def get_policy_version(self) -> str:
        pass

class DeferredAnalysisService:
    def enqueue_for_analysis(self, account_id: str, features: Dict[str, float]) -> None:
        pass

class LabelStore:
    def save_label(self, account_id: str, label: str, agreement: float, holdback: bool) -> None:
        pass

class MetricsService:
    def increment(self, metric_name: str) -> None:
        pass

    def record_value(self, metric_name: str, value: float) -> None:
        pass

@dataclass
class ActionEvent:
    action: ActionType
    reason: str
    policy_version: str
    rollback_ref: str

class ActionStore:
    def save_action(self, account_id: str, event: ActionEvent, idempotency_key: str) -> None:
        pass

# V3 Specific
class ConsensusNode:
    def propose_risk_state(self, account_id: str, score: float, confidence: float, action: ActionType) -> bool:
        pass

class ConsistentHashRouter:
    def get_route(self, account_id: str) -> str:
        pass

class CircuitBreaker:
    def __init__(self, threshold: int, reset_timeout_ms: int):
        self.threshold = threshold
        self.reset_timeout_ms = reset_timeout_ms
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.open = False

    def allow_request(self) -> bool:
        if self.open:
            if (time.time() * 1000) - self.last_failure_time > self.reset_timeout_ms:
                self.open = False
                self.failure_count = 0
                return True
            return False
        return True

    def record_success(self) -> None:
        if self.open:
            return
        self.failure_count = 0

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time() * 1000
        if self.failure_count >= self.threshold:
            self.open = True

    def is_open(self) -> bool:
        return self.open

@dataclass
class EvaluationResult:
    score: float
    confidence: float
    action: ActionType
    rollback_ref: str
    route_id: str

class DistributedBotDetectionService:
    AGREEMENT_THRESHOLD = 0.8

    def __init__(
        self,
        feature_service: FeatureService,
        rules_engine: RulesEngine,
        model_service: ModelService,
        anomaly_detector: AnomalyDetector,
        policy_engine: PolicyEngine,
        deferred_analysis_service: DeferredAnalysisService,
        label_store: LabelStore,
        metrics_service: MetricsService,
        action_store: ActionStore,
        router: ConsistentHashRouter,
        consensus_nodes: List[ConsensusNode],
        cluster_circuit_breaker: CircuitBreaker
    ):
        self.feature_service = feature_service
        self.rules_engine = rules_engine
        self.model_service = model_service
        self.anomaly_detector = anomaly_detector
        self.policy_engine = policy_engine
        self.deferred_analysis_service = deferred_analysis_service
        self.label_store = label_store
        self.metrics_service = metrics_service
        self.action_store = action_store
        self.router = router
        self.consensus_nodes = consensus_nodes
        self.cluster_circuit_breaker = cluster_circuit_breaker
        self.cluster_degraded = False

    def evaluate_account(self, account_id: str, event_id: str) -> EvaluationResult:
        start_time = time.time() * 1000

        route_id = self.router.get_route(account_id)
        self.metrics_service.increment(f"route.{route_id}")

        if not self.cluster_circuit_breaker.allow_request():
            self.cluster_degraded = True
            self.metrics_service.increment("cluster.degraded")
        else:
            self.cluster_degraded = False

        feature_result = self.feature_service.get_features(account_id)
        confidence = 1.0

        if feature_result.is_delayed:
            confidence -= 0.3
            self.metrics_service.increment("features.delayed")

        rule_result = self.rules_engine.evaluate(account_id, feature_result.features)

        final_score = 0.0

        if self.cluster_degraded:
            # Circuit breaker fallback to high-precision rules
            final_score = 0.9 if rule_result.matched_high_precision else 0.0
            confidence -= 0.5
            self.metrics_service.increment("eval.fallback.rules_only")
        else:
            model_result = self.model_service.evaluate(account_id, feature_result.features)
            if model_result.timed_out:
                self.cluster_circuit_breaker.record_failure()
                self.metrics_service.increment("model.timeout.degraded_mode")
                confidence -= 0.4
                final_score = 0.9 if rule_result.matched_high_precision else rule_result.score
                self.deferred_analysis_service.enqueue_for_analysis(account_id, feature_result.features)
            else:
                self.cluster_circuit_breaker.record_success()
                anomaly_score = self.anomaly_detector.get_anomaly_score(account_id, feature_result.features)
                final_score = (rule_result.score * 0.3) + (model_result.score * 0.5) + (anomaly_score * 0.2)
                if rule_result.matched_high_precision:
                    final_score = max(final_score, 0.9)

        decision = self.policy_engine.decide_action(final_score, confidence)

        # Consensus synchronization
        acks = 0
        for node in self.consensus_nodes:
            try:
                if node.propose_risk_state(account_id, final_score, confidence, decision.action):
                    acks += 1
            except Exception:
                pass # Ignore node failure

        if acks < (len(self.consensus_nodes) // 2) + 1:
            self.metrics_service.increment("consensus.failed")
            confidence -= 0.1

        rollback_ref = str(uuid.uuid4())
        idempotency_key = event_id

        action_event = ActionEvent(
            action=decision.action,
            reason=decision.reason,
            policy_version=self.policy_engine.get_policy_version(),
            rollback_ref=rollback_ref
        )
        self.action_store.save_action(account_id, action_event, idempotency_key)

        if decision.action in [ActionType.ROUTE_TO_REVIEW, ActionType.CHALLENGE] or confidence < 0.8:
            self.deferred_analysis_service.enqueue_for_analysis(account_id, feature_result.features)

        self.metrics_service.record_value("evaluation.latency.ms", (time.time() * 1000) - start_time)

        return EvaluationResult(
            score=final_score,
            confidence=confidence,
            action=decision.action,
            rollback_ref=rollback_ref,
            route_id=route_id
        )

    def submit_investigator_label(self, account_id: str, label: str, agreement_score: float) -> None:
        holdback = agreement_score < self.AGREEMENT_THRESHOLD
        if holdback:
            self.metrics_service.increment("label.held_back")
        else:
            self.metrics_service.increment("label.accepted")

        self.label_store.save_label(account_id, label, agreement_score, holdback)
