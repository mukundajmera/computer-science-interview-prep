import uuid
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Protocol

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

@dataclass
class RuleResult:
    score: float
    matched_high_precision: bool

@dataclass
class ModelResult:
    score: float
    timed_out: bool

@dataclass
class PolicyDecision:
    action: ActionType
    reason: str

@dataclass
class ActionEvent:
    action: ActionType
    reason: str
    policy_version: str
    rollback_ref: str

@dataclass
class EvaluationResult:
    score: float
    confidence: float
    action: ActionType
    rollback_ref: str

class FeatureService(Protocol):
    def get_features(self, account_id: str) -> FeatureResult:
        ...

class RulesEngine(Protocol):
    def evaluate(self, account_id: str, features: Dict[str, float]) -> RuleResult:
        ...

class ModelService(Protocol):
    def evaluate(self, account_id: str, features: Dict[str, float]) -> ModelResult:
        ...

class AnomalyDetector(Protocol):
    def get_anomaly_score(self, account_id: str, features: Dict[str, float]) -> float:
        ...

class PolicyEngine(Protocol):
    def decide_action(self, risk_score: float, confidence: float) -> PolicyDecision:
        ...

    def get_policy_version(self) -> str:
        ...

class DeferredAnalysisService(Protocol):
    def enqueue_for_analysis(self, account_id: str, features: Dict[str, float]) -> None:
        ...

class LabelStore(Protocol):
    def save_label(self, account_id: str, label: str, agreement: float, holdback: bool) -> None:
        ...

class MetricsService(Protocol):
    def increment(self, metric_name: str) -> None:
        ...

    def record_value(self, metric_name: str, value: float) -> None:
        ...

class ActionStore(Protocol):
    def save_action(self, account_id: str, event: ActionEvent) -> None:
        ...

class ScaledBotDetectionService:
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

    def evaluate_account(self, account_id: str) -> EvaluationResult:
        start_time = time.time()

        feature_result = self.feature_service.get_features(account_id)
        confidence = 1.0

        if feature_result.is_delayed:
            confidence -= 0.3  # Lower confidence on delayed/fallback features
            self.metrics_service.increment("features.delayed")

        rule_result = self.rules_engine.evaluate(account_id, feature_result.features)
        model_result = self.model_service.evaluate(account_id, feature_result.features)

        final_score = 0.0
        if model_result.timed_out:
            self.metrics_service.increment("model.timeout.degraded_mode")
            confidence -= 0.4
            # In degraded mode, rely on high precision rules
            final_score = 0.9 if rule_result.matched_high_precision else rule_result.score
        else:
            anomaly_score = self.anomaly_detector.get_anomaly_score(account_id, feature_result.features)
            # Combine scores (simplified ensemble logic)
            final_score = (rule_result.score * 0.3) + (model_result.score * 0.5) + (anomaly_score * 0.2)
            if rule_result.matched_high_precision:
                final_score = max(final_score, 0.9)

        decision = self.policy_engine.decide_action(final_score, confidence)

        rollback_ref = str(uuid.uuid4())
        action_event = ActionEvent(
            action=decision.action,
            reason=decision.reason,
            policy_version=self.policy_engine.get_policy_version(),
            rollback_ref=rollback_ref
        )
        self.action_store.save_action(account_id, action_event)

        if decision.action in (ActionType.ROUTE_TO_REVIEW, ActionType.CHALLENGE) or confidence < 0.8:
            self.deferred_analysis_service.enqueue_for_analysis(account_id, feature_result.features)

        latency_ms = (time.time() - start_time) * 1000
        self.metrics_service.record_value("evaluation.latency.ms", latency_ms)

        return EvaluationResult(
            score=final_score,
            confidence=confidence,
            action=decision.action,
            rollback_ref=rollback_ref
        )

    def submit_investigator_label(self, account_id: str, label: str, agreement_score: float) -> None:
        holdback = agreement_score < self.AGREEMENT_THRESHOLD
        if holdback:
            self.metrics_service.increment("label.held_back")
        else:
            self.metrics_service.increment("label.accepted")

        self.label_store.save_label(account_id, label, agreement_score, holdback)
