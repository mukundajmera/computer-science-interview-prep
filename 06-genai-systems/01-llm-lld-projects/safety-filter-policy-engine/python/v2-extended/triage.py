"""Policy and decision models for calibrated moderation triage."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrecisionGuardrail:
    """Threshold policy for confidence-aware triage decisions."""

    demote_threshold: float = 0.40
    review_threshold: float = 0.65
    auto_block_threshold: float = 0.90
    min_confidence_for_block: float = 0.90

    def __post_init__(self) -> None:
        values = [
            self.demote_threshold,
            self.review_threshold,
            self.auto_block_threshold,
            self.min_confidence_for_block,
        ]
        if any(v < 0 or v > 1 for v in values):
            raise ValueError("All thresholds must be in [0, 1]")
        if not (self.demote_threshold <= self.review_threshold <= self.auto_block_threshold):
            raise ValueError("Expected demote <= review <= auto_block")


@dataclass
class TriageDecision:
    """Decision envelope for multi-stage moderation actions."""

    action: str
    score: float
    confidence: float
    reason: str
    queue: str | None = None
