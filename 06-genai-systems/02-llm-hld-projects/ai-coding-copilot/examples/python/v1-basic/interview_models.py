"""Core interview session models for AI coding interview examples."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class InterviewFormat(Enum):
    """Supported interview formats."""

    STRUCTURED = "structured"
    OPEN_ENDED = "open_ended"


class InterviewPhase(Enum):
    """High-level phases in an AI-enabled coding round."""

    ORIENTATION = "orientation"
    IMPLEMENT = "implement"
    VERIFY = "verify"
    OPTIMIZE = "optimize"


class RubricDimension(Enum):
    """Execution rubric dimensions."""

    APPROACH = "approach"
    CONTROL = "control"
    VERIFICATION = "verification"
    COMMUNICATION = "communication"


@dataclass
class SessionEvent:
    """One logged action in the session timeline."""

    event_type: str
    detail: str


@dataclass
class RubricScore:
    """Current rubric snapshot."""

    scores: Dict[RubricDimension, int] = field(default_factory=dict)


@dataclass
class InterviewSession:
    """Mutable session state for orchestration examples."""

    session_id: str
    interview_format: InterviewFormat
    current_phase: InterviewPhase
    events: List[SessionEvent] = field(default_factory=list)
    rubric_score: RubricScore = field(default_factory=RubricScore)
