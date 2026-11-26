"""v3-production: idempotent start + checkpoint resume."""

from typing import Callable, Dict


class DurableWorkflowOrchestrator:
    def __init__(self) -> None:
        self._checkpoint_by_workflow: Dict[str, int] = {}
        self._idempotency_to_workflow: Dict[str, str] = {}

    def start(self, idempotency_key: str, workflow_id: str) -> str:
        existing = self._idempotency_to_workflow.get(idempotency_key)
        if existing is not None:
            return existing
        self._idempotency_to_workflow[idempotency_key] = workflow_id
        self._checkpoint_by_workflow[workflow_id] = 0
        return workflow_id

    def checkpoint(self, workflow_id: str, checkpoint: int) -> None:
        self._checkpoint_by_workflow[workflow_id] = checkpoint

    def resume(self, workflow_id: str, handler: Callable[[str, int], None]) -> None:
        checkpoint = self._checkpoint_by_workflow.get(workflow_id, 0)
        handler(workflow_id, checkpoint)
