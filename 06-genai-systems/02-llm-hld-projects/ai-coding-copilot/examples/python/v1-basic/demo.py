"""Demonstrates a simple AI coding interview session lifecycle."""

from interview_models import InterviewFormat, InterviewPhase, RubricDimension
from interview_orchestrator import InterviewSessionOrchestrator


def main() -> None:
    orchestrator = InterviewSessionOrchestrator()
    session = orchestrator.startSession("demo-1", InterviewFormat.STRUCTURED)

    orchestrator.recordAiAction(session, "Asked AI for interface skeleton only")
    orchestrator.transitionPhase(session, InterviewPhase.IMPLEMENT)
    orchestrator.recordVerificationEvent(session, "Ran unit tests for changed module")
    orchestrator.transitionPhase(session, InterviewPhase.VERIFY)

    orchestrator.recordRubricObservation(session, RubricDimension.APPROACH, 4)
    orchestrator.recordRubricObservation(session, RubricDimension.CONTROL, 5)
    orchestrator.recordRubricObservation(session, RubricDimension.VERIFICATION, 4)
    orchestrator.recordRubricObservation(session, RubricDimension.COMMUNICATION, 4)

    summary = orchestrator.sessionSummary(session)
    print(summary)


if __name__ == "__main__":
    main()
