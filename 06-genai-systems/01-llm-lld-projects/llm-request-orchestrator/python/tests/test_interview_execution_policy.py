"""Unit tests for interview execution policy."""

import os
import sys
import unittest

# ---------------------------------------------------------------------------
# Path setup – ensure the v1-basic package is importable
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_v1_dir = os.path.join(os.path.dirname(_here), "v1-basic")
if _v1_dir not in sys.path:
    sys.path.insert(0, _v1_dir)

from interview_execution_policy import (  # noqa: E402
    ExecutionState,
    InterviewExecutionPolicy,
    InterviewPhase,
    RecommendedAction,
    build_prompt_template,
    phase_checklist,
)


class TestInterviewExecutionPolicy(unittest.TestCase):
    """Tests recommendation priority and branch behavior."""

    def setUp(self) -> None:
        self.policy = InterviewExecutionPolicy()

    def test_alignment_is_first_gate(self) -> None:
        state = ExecutionState()
        rec = self.policy.recommend_next_action(state)
        self.assertEqual(rec.phase, InterviewPhase.ALIGNMENT)
        self.assertEqual(rec.action, RecommendedAction.CONFIRM_ALIGNMENT)

    def test_ai_miss_priority_after_alignment(self) -> None:
        state = ExecutionState(
            alignment_confirmed=True,
            ai_miss_detected=True,
            ai_miss_resolved=False,
        )
        rec = self.policy.recommend_next_action(state)
        self.assertEqual(rec.phase, InterviewPhase.AI_MISS_RECOVERY)
        self.assertEqual(rec.action, RecommendedAction.HANDLE_AI_MISS)

    def test_build_branch_when_build_not_succeeded(self) -> None:
        state = ExecutionState(alignment_confirmed=True, ai_miss_resolved=True)
        rec = self.policy.recommend_next_action(state)
        self.assertEqual(rec.phase, InterviewPhase.BUILD)
        self.assertEqual(rec.action, RecommendedAction.FIX_BUILD)

    def test_tests_branch_when_build_done(self) -> None:
        state = ExecutionState(
            alignment_confirmed=True,
            build_succeeded=True,
            ai_miss_resolved=True,
        )
        rec = self.policy.recommend_next_action(state)
        self.assertEqual(rec.phase, InterviewPhase.TESTS)
        self.assertEqual(rec.action, RecommendedAction.FIX_TESTS)

    def test_types_branch_when_tests_done(self) -> None:
        state = ExecutionState(
            alignment_confirmed=True,
            build_succeeded=True,
            tests_passed=True,
            ai_miss_resolved=True,
        )
        rec = self.policy.recommend_next_action(state)
        self.assertEqual(rec.phase, InterviewPhase.TYPES)
        self.assertEqual(rec.action, RecommendedAction.FIX_TYPES)

    def test_finalization_when_all_gates_pass(self) -> None:
        state = ExecutionState(
            alignment_confirmed=True,
            build_succeeded=True,
            tests_passed=True,
            types_passed=True,
            ai_miss_resolved=True,
        )
        rec = self.policy.recommend_next_action(state)
        self.assertEqual(rec.phase, InterviewPhase.FINALIZATION)
        self.assertEqual(rec.action, RecommendedAction.PREPARE_FINAL_RESPONSE)


class TestInterviewExecutionPolicyHelpers(unittest.TestCase):
    """Tests helper methods for prompt generation and checklists."""

    def test_phase_checklist_returns_expected_items(self) -> None:
        checklist = phase_checklist(InterviewPhase.BUILD)
        self.assertIsInstance(checklist, tuple)
        self.assertGreaterEqual(len(checklist), 3)
        self.assertIn("Run compile/build flow for touched modules.", checklist)

    def test_prompt_template_contains_phase_checklist_and_sorted_context(self) -> None:
        prompt = build_prompt_template(
            InterviewPhase.ALIGNMENT,
            context={"zeta": "2", "alpha": "1"},
        )
        self.assertIn("Phase: ALIGNMENT", prompt)
        self.assertIn("Checklist:", prompt)
        self.assertLess(prompt.find("- alpha: 1"), prompt.find("- zeta: 2"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
