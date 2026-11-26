"""Interview session orchestrator for AI coding execution drills."""

from typing import Dict

from interview_models import (
    InterviewFormat,
    InterviewPhase,
    InterviewSession,
    RubricDimension,
    RubricScore,
    SessionEvent,
)


class InterviewSessionOrchestrator:
    """Orchestrates phase transitions, event logging, and rubric snapshots."""

    def startSession(self, session_id: str, interview_format: InterviewFormat) -> InterviewSession:
        """Create a new session starting in orientation phase."""
        return InterviewSession(
            session_id=session_id,
            interview_format=interview_format,
            current_phase=InterviewPhase.ORIENTATION,
        )

    def transitionPhase(self, session: InterviewSession, next_phase: InterviewPhase) -> None:
        """Move session to a new phase and log transition."""
        session.current_phase = next_phase
        session.events.append(SessionEvent(event_type="phase_transition", detail=next_phase.value))

    def recordAiAction(self, session: InterviewSession, prompt_summary: str) -> None:
        """Log an AI action summary."""
        session.events.append(SessionEvent(event_type="ai_action", detail=prompt_summary))

    def recordVerificationEvent(self, session: InterviewSession, verification_summary: str) -> None:
        """Log a verification action summary."""
        session.events.append(
            SessionEvent(event_type="verification_event", detail=verification_summary)
        )

    def recordRubricObservation(
        self,
        session: InterviewSession,
        dimension: RubricDimension,
        score: int,
    ) -> None:
        """Record a rubric score from 1 to 5 for a dimension."""
        if score < 1 or score > 5:
            raise ValueError("score must be between 1 and 5")
        session.rubric_score.scores[dimension] = score

    def sessionSummary(self, session: InterviewSession) -> Dict[str, object]:
        """Return a compact summary useful for drill review."""
        rubric_raw = session.rubric_score.scores
        average = 0.0
        if rubric_raw:
            average = sum(rubric_raw.values()) / len(rubric_raw)

        return {
            "session_id": session.session_id,
            "format": session.interview_format.value,
            "phase": session.current_phase.value,
            "events": len(session.events),
            "rubric_average": round(average, 2),
        }
