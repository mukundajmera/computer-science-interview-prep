"""Interview execution policy for deterministic next-step recommendations."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Mapping, Tuple


class InterviewPhase(Enum):
    """Ordered phases for interview execution."""

    ALIGNMENT = "ALIGNMENT"
    AI_MISS_RECOVERY = "AI_MISS_RECOVERY"
    BUILD = "BUILD"
    TESTS = "TESTS"
    TYPES = "TYPES"
    FINALIZATION = "FINALIZATION"


class RecommendedAction(Enum):
    """Action labels returned by the execution policy."""

    CONFIRM_ALIGNMENT = "CONFIRM_ALIGNMENT"
    HANDLE_AI_MISS = "HANDLE_AI_MISS"
    FIX_BUILD = "FIX_BUILD"
    FIX_TESTS = "FIX_TESTS"
    FIX_TYPES = "FIX_TYPES"
    PREPARE_FINAL_RESPONSE = "PREPARE_FINAL_RESPONSE"


@dataclass(frozen=True)
class ExecutionState:
    """Snapshot of execution status used for policy decisions."""

    alignment_confirmed: bool = False
    build_succeeded: bool = False
    tests_passed: bool = False
    types_passed: bool = False
    ai_miss_detected: bool = False
    ai_miss_resolved: bool = True
    context: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyRecommendation:
    """Recommended next step and supporting metadata."""

    phase: InterviewPhase
    action: RecommendedAction
    rationale: str
    checklist: Tuple[str, ...]


_PHASE_CHECKLISTS: Dict[InterviewPhase, Tuple[str, ...]] = {
    InterviewPhase.ALIGNMENT: (
        "Restate user intent and constraints.",
        "Identify missing requirements and assumptions.",
        "Confirm implementation scope before editing.",
    ),
    InterviewPhase.AI_MISS_RECOVERY: (
        "Acknowledge AI miss explicitly.",
        "Locate failing assumption or mismatch.",
        "Apply corrective action and re-validate affected path.",
    ),
    InterviewPhase.BUILD: (
        "Run compile/build flow for touched modules.",
        "Fix syntax/import/runtime wiring issues.",
        "Re-run build until clean.",
    ),
    InterviewPhase.TESTS: (
        "Run deterministic unit tests.",
        "Fix regressions with minimal surface-area change.",
        "Re-run relevant tests to verify.",
    ),
    InterviewPhase.TYPES: (
        "Run static typing checks (if configured).",
        "Fix annotation or interface mismatches.",
        "Re-run type checks for touched scope.",
    ),
    InterviewPhase.FINALIZATION: (
        "Summarize what changed and why.",
        "Report tests/checks executed and outcomes.",
        "Flag residual risks or follow-ups.",
    ),
}


class InterviewExecutionPolicy:
    """Deterministic policy for selecting the next execution action."""

    def recommend_next_action(self, state: ExecutionState) -> PolicyRecommendation:
        """Return the highest-priority next action based on current state."""
        if not state.alignment_confirmed:
            return self._recommend(
                InterviewPhase.ALIGNMENT,
                RecommendedAction.CONFIRM_ALIGNMENT,
                "Alignment is not yet confirmed.",
            )

        if state.ai_miss_detected and not state.ai_miss_resolved:
            return self._recommend(
                InterviewPhase.AI_MISS_RECOVERY,
                RecommendedAction.HANDLE_AI_MISS,
                "AI miss is active and unresolved.",
            )

        if not state.build_succeeded:
            return self._recommend(
                InterviewPhase.BUILD,
                RecommendedAction.FIX_BUILD,
                "Build is failing or not yet validated.",
            )

        if not state.tests_passed:
            return self._recommend(
                InterviewPhase.TESTS,
                RecommendedAction.FIX_TESTS,
                "Tests have not passed.",
            )

        if not state.types_passed:
            return self._recommend(
                InterviewPhase.TYPES,
                RecommendedAction.FIX_TYPES,
                "Type checks have not passed.",
            )

        return self._recommend(
            InterviewPhase.FINALIZATION,
            RecommendedAction.PREPARE_FINAL_RESPONSE,
            "All gates passed; prepare final response.",
        )

    def build_prompt_template(
        self,
        phase: InterviewPhase,
        context: Mapping[str, str] | None = None,
    ) -> str:
        """Build a prompt template with phase-focused checklist and context."""
        lines = [f"Phase: {phase.value}", "Checklist:"]
        for item in self.phase_checklist(phase):
            lines.append(f"- {item}")
        if context:
            lines.append("Context:")
            for key in sorted(context.keys()):
                lines.append(f"- {key}: {context[key]}")
        return "\n".join(lines)

    def phase_checklist(self, phase: InterviewPhase) -> Tuple[str, ...]:
        """Return the immutable checklist for a given phase."""
        return _PHASE_CHECKLISTS[phase]

    def _recommend(
        self,
        phase: InterviewPhase,
        action: RecommendedAction,
        rationale: str,
    ) -> PolicyRecommendation:
        return PolicyRecommendation(
            phase=phase,
            action=action,
            rationale=rationale,
            checklist=self.phase_checklist(phase),
        )


def phase_checklist(phase: InterviewPhase) -> Tuple[str, ...]:
    """Convenience helper to fetch per-phase checklist items."""
    return InterviewExecutionPolicy().phase_checklist(phase)


def build_prompt_template(
    phase: InterviewPhase,
    context: Mapping[str, str] | None = None,
) -> str:
    """Convenience helper to generate a phase prompt template."""
    return InterviewExecutionPolicy().build_prompt_template(phase, context=context)
