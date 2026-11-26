"""Demo for confidence-aware moderation triage."""

from __future__ import annotations

from engine_v2 import TriageEngine
from triage import PrecisionGuardrail


def main() -> None:
    guardrail = PrecisionGuardrail(
        demote_threshold=0.35,
        review_threshold=0.60,
        auto_block_threshold=0.88,
        min_confidence_for_block=0.90,
    )
    engine = TriageEngine(guardrail)

    examples = [
        (0.20, 0.80),
        (0.50, 0.70),
        (0.75, 0.65),
        (0.93, 0.95),
        (0.93, 0.70),
    ]

    for score, confidence in examples:
        decision = engine.decide(score, confidence, risk_context="feed")
        print(decision, "->", engine.map_to_v1_action(decision.action))


if __name__ == "__main__":
    main()
