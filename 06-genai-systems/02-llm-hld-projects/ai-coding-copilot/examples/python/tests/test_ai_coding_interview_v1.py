"""Tests for AI coding interview session orchestration example."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))

from interview_models import InterviewFormat, InterviewPhase, RubricDimension
from interview_orchestrator import InterviewSessionOrchestrator


class TestAICodingInterviewV1(unittest.TestCase):
    """Validates core session orchestration behaviors."""

    def setUp(self) -> None:
        self.orchestrator = InterviewSessionOrchestrator()

    def test_start_session_defaults(self) -> None:
        session = self.orchestrator.startSession("s1", InterviewFormat.OPEN_ENDED)
        self.assertEqual(session.session_id, "s1")
        self.assertEqual(session.interview_format, InterviewFormat.OPEN_ENDED)
        self.assertEqual(session.current_phase, InterviewPhase.ORIENTATION)

    def test_phase_transition_and_event_logging(self) -> None:
        session = self.orchestrator.startSession("s2", InterviewFormat.STRUCTURED)
        self.orchestrator.transitionPhase(session, InterviewPhase.IMPLEMENT)
        self.assertEqual(session.current_phase, InterviewPhase.IMPLEMENT)
        self.assertEqual(len(session.events), 1)
        self.assertEqual(session.events[0].event_type, "phase_transition")

    def test_rubric_bounds(self) -> None:
        session = self.orchestrator.startSession("s3", InterviewFormat.STRUCTURED)
        with self.assertRaises(ValueError):
            self.orchestrator.recordRubricObservation(session, RubricDimension.APPROACH, 0)
        self.orchestrator.recordRubricObservation(session, RubricDimension.APPROACH, 5)
        summary = self.orchestrator.sessionSummary(session)
        self.assertEqual(summary["rubric_average"], 5.0)


if __name__ == "__main__":
    unittest.main()
