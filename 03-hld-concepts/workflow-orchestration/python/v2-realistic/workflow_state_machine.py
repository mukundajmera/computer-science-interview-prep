"""v2-realistic: workflow lifecycle state machine."""

from enum import Enum
from typing import Dict


class WorkflowState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPENSATING = "compensating"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class WorkflowStateMachine:
    def __init__(self) -> None:
        self._state_by_workflow: Dict[str, WorkflowState] = {}

    def create(self, workflow_id: str) -> None:
        self._state_by_workflow[workflow_id] = WorkflowState.CREATED

    def mark_running(self, workflow_id: str) -> None:
        self._state_by_workflow[workflow_id] = WorkflowState.RUNNING

    def mark_compensating(self, workflow_id: str) -> None:
        self._state_by_workflow[workflow_id] = WorkflowState.COMPENSATING

    def mark_succeeded(self, workflow_id: str) -> None:
        self._state_by_workflow[workflow_id] = WorkflowState.SUCCEEDED

    def mark_failed(self, workflow_id: str) -> None:
        self._state_by_workflow[workflow_id] = WorkflowState.FAILED

    def get(self, workflow_id: str) -> WorkflowState:
        return self._state_by_workflow[workflow_id]
