import uuid
import sys
import os

# Add src to sys.path so we can import from saga
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from saga import (
    SagaStep, SagaContext, SagaOrchestratorEngine,
    TransactionalOutboxRelay, OutboxEvent, InboxConsumer
)

class MockStep(SagaStep):
    def __init__(self, name: str, is_pivot: bool, fail_execute: bool = False, fail_compensate: bool = False):
        super().__init__(name, is_pivot)
        self.fail_execute = fail_execute
        self.fail_compensate = fail_compensate
        self.executed = False
        self.compensated = False

    def execute(self, context: SagaContext) -> bool:
        self.executed = True
        return not self.fail_execute

    def compensate(self, context: SagaContext) -> bool:
        self.compensated = True
        return not self.fail_compensate

def test_forward_execution_success():
    s1 = MockStep("CreateOrder", False)
    s2 = MockStep("ProcessPayment", False)
    s3 = MockStep("ReserveInventory", True)
    s4 = MockStep("ScheduleShipping", False)
    
    engine = SagaOrchestratorEngine([s1, s2, s3, s4])
    context = engine.execute_saga(str(uuid.uuid4()))
    
    assert context.final_status == "COMPLETED"
    assert len(context.completed_steps) == 4
    assert all([s1.executed, s2.executed, s3.executed, s4.executed])
    assert not any([s1.compensated, s2.compensated, s3.compensated, s4.compensated])

def test_mid_step_compensation_rollback():
    s1 = MockStep("CreateOrder", False)
    s2 = MockStep("ProcessPayment", False)
    s3 = MockStep("ReserveInventory", True, fail_execute=True)
    
    engine = SagaOrchestratorEngine([s1, s2, s3])
    context = engine.execute_saga(str(uuid.uuid4()))
    
    assert context.final_status == "CANCELLED"
    assert context.is_compensating
    assert s3.executed
    assert s2.compensated
    assert s1.compensated
    assert not s3.compensated

def test_pivot_step_commitment_and_retriable_failure():
    s1 = MockStep("CreateOrder", False)
    s2 = MockStep("ReserveInventory", True)  # Pivot
    s3 = MockStep("ScheduleShipping", False, fail_execute=True)
    
    engine = SagaOrchestratorEngine([s1, s2, s3])
    context = engine.execute_saga(str(uuid.uuid4()))
    
    assert context.final_status == "FAILED_REQUIRES_RETRY"
    assert not context.is_compensating
    assert all([s1.executed, s2.executed, s3.executed])
    assert not any([s1.compensated, s2.compensated, s3.compensated])

def test_outbox_event_deduplication():
    relay = TransactionalOutboxRelay()
    event_id = str(uuid.uuid4())
    
    relay.insert_event(OutboxEvent(event_id, "Order", "OrderCreated"))
    relay.relay_events()
    
    relay.insert_event(OutboxEvent(event_id, "Order", "OrderCreated"))
    relay.relay_events()
    
    published = relay.get_published_events()
    assert len(published) == 2
    
    consumer = InboxConsumer()
    
    first_consume = consumer.consume_event(published[0].event_id, published[0].payload)
    assert first_consume is True
    
    second_consume = consumer.consume_event(published[1].event_id, published[1].payload)
    assert second_consume is False
    
    assert len(consumer.get_processed_items()) == 1
    assert consumer.get_processed_items()[0] == "OrderCreated"
