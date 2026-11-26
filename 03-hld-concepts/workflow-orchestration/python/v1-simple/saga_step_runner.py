"""v1-simple: execute steps and compensate on failure."""

from dataclasses import dataclass, field
from typing import List, Protocol


class WorkflowStep(Protocol):
    def name(self) -> str: ...
    def execute(self) -> None: ...
    def compensate(self) -> None: ...


@dataclass
class ExecutionResult:
    success: bool
    message: str
    compensated_steps: List[str] = field(default_factory=list)


class SagaStepRunner:
    def run(self, steps: List[WorkflowStep]) -> ExecutionResult:
        completed: List[WorkflowStep] = []
        try:
            for step in steps:
                step.execute()
                completed.append(step)
            return ExecutionResult(success=True, message="completed")
        except RuntimeError as exc:
            for step in reversed(completed):
                step.compensate()
            return ExecutionResult(
                success=False,
                message=str(exc),
                compensated_steps=[step.name() for step in completed],
            )
