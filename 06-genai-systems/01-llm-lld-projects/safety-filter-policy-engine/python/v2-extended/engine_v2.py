"""Engine wrapper for calibrated triage decisions."""

from __future__ import annotations

from dataclasses import dataclass

from calibration import DecisionCalibrator
from triage import PrecisionGuardrail, TriageDecision


@dataclass
class EscalationDecision:
    """Decision used by orchestration layers outside v1 filter engine."""

    action: str
    queue: str | None
    reason: str
    score: float
    confidence: float


class TriageEngine:
    """Thin orchestration layer over the decision calibrator."""

    def __init__(self, guardrail: PrecisionGuardrail, calibrator: DecisionCalibrator | None = None) -> None:
        self.guardrail = guardrail
        self.calibrator = calibrator or DecisionCalibrator()

    def decide(self, score: float, confidence: float, risk_context: str = "default") -> EscalationDecision:
        """Produce an escalation decision for downstream moderation workflows."""
        routed: TriageDecision = self.calibrator.route(score, confidence, self.guardrail, risk_context)
        return EscalationDecision(
            action=routed.action,
            queue=routed.queue,
            reason=routed.reason,
            score=routed.score,
            confidence=routed.confidence,
        )

    @staticmethod
    def map_to_v1_action(decision_action: str) -> str:
        """Map v2 decision actions into v1-compatible action labels.

        v1 supports ALLOW/FLAG/BLOCK. v2 demote/review map to FLAG.
        """
        normalized = decision_action.lower()
        if normalized == "allow":
            return "ALLOW"
        if normalized == "block":
            return "BLOCK"
        if normalized in {"demote", "review"}:
            return "FLAG"
        raise ValueError(f"Unknown decision action: {decision_action}")
