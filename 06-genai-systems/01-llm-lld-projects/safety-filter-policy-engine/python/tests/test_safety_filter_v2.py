"""Tests for safety-filter-policy-engine v2 triage helpers."""

import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "v2-extended",
    ),
)


class TestPrecisionGuardrail(unittest.TestCase):
    def test_invalid_order_raises(self) -> None:
        from triage import PrecisionGuardrail

        with self.assertRaises(ValueError):
            PrecisionGuardrail(demote_threshold=0.7, review_threshold=0.6)


class TestDecisionCalibrator(unittest.TestCase):
    def setUp(self) -> None:
        from calibration import DecisionCalibrator
        from triage import PrecisionGuardrail

        self.calibrator = DecisionCalibrator()
        self.guardrail = PrecisionGuardrail(
            demote_threshold=0.4,
            review_threshold=0.65,
            auto_block_threshold=0.9,
            min_confidence_for_block=0.9,
        )

    def test_block_when_high_score_and_confidence(self) -> None:
        decision = self.calibrator.route(0.95, 0.95, self.guardrail)
        self.assertEqual(decision.action, "block")

    def test_review_when_high_score_low_confidence(self) -> None:
        decision = self.calibrator.route(0.95, 0.70, self.guardrail, risk_context="feed")
        self.assertEqual(decision.action, "review")
        self.assertEqual(decision.queue, "review:feed")

    def test_demote_band(self) -> None:
        decision = self.calibrator.route(0.5, 0.8, self.guardrail)
        self.assertEqual(decision.action, "demote")

    def test_allow_band(self) -> None:
        decision = self.calibrator.route(0.2, 0.9, self.guardrail)
        self.assertEqual(decision.action, "allow")


class TestTriageEngine(unittest.TestCase):
    def test_map_to_v1_action(self) -> None:
        from engine_v2 import TriageEngine

        self.assertEqual(TriageEngine.map_to_v1_action("allow"), "ALLOW")
        self.assertEqual(TriageEngine.map_to_v1_action("demote"), "FLAG")
        self.assertEqual(TriageEngine.map_to_v1_action("review"), "FLAG")
        self.assertEqual(TriageEngine.map_to_v1_action("block"), "BLOCK")


if __name__ == "__main__":
    unittest.main()
