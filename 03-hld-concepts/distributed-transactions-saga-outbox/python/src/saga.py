from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
import uuid

@dataclass
class SagaContext:
    saga_id: str
    completed_steps: List[str] = field(default_factory=list)
    is_compensating: bool = False
    final_status: str = "PENDING"

class SagaStep:
    def __init__(self, name: str, is_pivot: bool):
        self.name = name
        self.is_pivot = is_pivot

    def execute(self, context: SagaContext) -> bool:
        raise NotImplementedError

    def compensate(self, context: SagaContext) -> bool:
        raise NotImplementedError

class SagaOrchestratorEngine:
    def __init__(self, steps: List[SagaStep]):
        self.steps = steps

    def execute_saga(self, saga_id: str) -> SagaContext:
        context = SagaContext(saga_id=saga_id)
        
        for i, step in enumerate(self.steps):
            success = step.execute(context)
            if success:
                context.completed_steps.append(step.name)
            else:
                passed_pivot = any(
                    s.is_pivot for s in self.steps if s.name in context.completed_steps
                )
                
                if passed_pivot:
                    context.final_status = "FAILED_REQUIRES_RETRY"
                    return context
                else:
                    context.is_compensating = True
                    self._compensate(context, i - 1)
                    return context

        context.final_status = "COMPLETED"
        return context

    def _compensate(self, context: SagaContext, last_successful_index: int):
        for i in range(last_successful_index, -1, -1):
            step = self.steps[i]
            comp_success = step.compensate(context)
            if not comp_success:
                context.final_status = "COMPENSATION_FAILED"
                return
        context.final_status = "CANCELLED"


@dataclass
class OutboxEvent:
    event_id: str
    aggregate_type: str
    payload: str

class TransactionalOutboxRelay:
    def __init__(self):
        self.outbox_table: List[OutboxEvent] = []
        self.published_log: List[OutboxEvent] = []

    def insert_event(self, event: OutboxEvent):
        """Called within local transaction."""
        self.outbox_table.append(event)

    def relay_events(self):
        """Called by CDC asynchronously."""
        for event in self.outbox_table:
            self._publish_to_broker(event)
        self.outbox_table.clear()

    def _publish_to_broker(self, event: OutboxEvent):
        self.published_log.append(event)

    def get_published_events(self) -> List[OutboxEvent]:
        return list(self.published_log)


class InboxConsumer:
    def __init__(self):
        self.inbox_table: Set[str] = set()
        self.processed_business_logic: List[str] = []

    def consume_event(self, event_id: str, payload: str) -> bool:
        if event_id in self.inbox_table:
            return False
            
        self.inbox_table.add(event_id)
        self.processed_business_logic.append(payload)
        return True

    def get_processed_items(self) -> List[str]:
        return list(self.processed_business_logic)
