"""Calibration logic for routing moderation outcomes."""

from __future__ import annotations

from triage import PrecisionGuardrail, TriageDecision


class DecisionCalibrator:
    """Maps score/confidence pairs to triage actions under guardrails."""

    def route(
        self,
        score: float,
        confidence: float,
        guardrail: PrecisionGuardrail,
        risk_context: str = "default",
    ) -> TriageDecision:
        """Return triage decision using score + confidence + threshold policy."""
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be in [0, 1]")

        if score >= guardrail.auto_block_threshold:
            if confidence >= guardrail.min_confidence_for_block:
                return TriageDecision("block", score, confidence, "high_score_high_confidence")
            return TriageDecision("review", score, confidence, "high_score_low_confidence", queue=f"review:{risk_context}")

        if score >= guardrail.review_threshold:
            return TriageDecision("review", score, confidence, "review_band", queue=f"review:{risk_context}")

        if score >= guardrail.demote_threshold:
            return TriageDecision("demote", score, confidence, "demote_band")

        return TriageDecision("allow", score, confidence, "below_threshold")
