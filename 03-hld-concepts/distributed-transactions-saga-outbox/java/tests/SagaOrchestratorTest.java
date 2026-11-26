import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

class SagaOrchestratorTest {
    
    static class MockStep extends SagaModels.SagaStep {
        boolean shouldFailExecute;
        boolean shouldFailCompensate;
        boolean executed = false;
        boolean compensated = false;

        public MockStep(String name, boolean isPivot, boolean shouldFailExecute, boolean shouldFailCompensate) {
            super(name, isPivot);
            this.shouldFailExecute = shouldFailExecute;
            this.shouldFailCompensate = shouldFailCompensate;
        }

        @Override
        public boolean execute(SagaModels.SagaContext context) {
            executed = true;
            return !shouldFailExecute;
        }

        @Override
        public boolean compensate(SagaModels.SagaContext context) {
            compensated = true;
            return !shouldFailCompensate;
        }
    }

    @Test
    void testForwardExecutionSuccess() {
        MockStep s1 = new MockStep("CreateOrder", false, false, false);
        MockStep s2 = new MockStep("ProcessPayment", false, false, false);
        MockStep s3 = new MockStep("ReserveInventory", true, false, false);
        MockStep s4 = new MockStep("ScheduleShipping", false, false, false);

        SagaOrchestratorEngine engine = new SagaOrchestratorEngine(Arrays.asList(s1, s2, s3, s4));
        SagaModels.SagaContext context = engine.executeSaga(UUID.randomUUID().toString());

        assertEquals("COMPLETED", context.finalStatus);
        assertEquals(4, context.completedSteps.size());
        assertTrue(s1.executed && s2.executed && s3.executed && s4.executed);
        assertFalse(s1.compensated || s2.compensated || s3.compensated || s4.compensated);
    }

    @Test
    void testMidStepCompensationRollback() {
        MockStep s1 = new MockStep("CreateOrder", false, false, false);
        MockStep s2 = new MockStep("ProcessPayment", false, false, false);
        MockStep s3 = new MockStep("ReserveInventory", true, true, false); // Fails here (before pivot completes)

        SagaOrchestratorEngine engine = new SagaOrchestratorEngine(Arrays.asList(s1, s2, s3));
        SagaModels.SagaContext context = engine.executeSaga(UUID.randomUUID().toString());

        assertEquals("CANCELLED", context.finalStatus);
        assertTrue(context.isCompensating);
        assertTrue(s3.executed); 
        // s2 and s1 should be compensated
        assertTrue(s2.compensated);
        assertTrue(s1.compensated);
        // s3 failed, so it shouldn't be compensated
        assertFalse(s3.compensated);
    }

    @Test
    void testPivotStepCommitmentAndRetriableFailure() {
        MockStep s1 = new MockStep("CreateOrder", false, false, false);
        MockStep s2 = new MockStep("ReserveInventory", true, false, false); // Pivot
        MockStep s3 = new MockStep("ScheduleShipping", false, true, false); // Fails after pivot

        SagaOrchestratorEngine engine = new SagaOrchestratorEngine(Arrays.asList(s1, s2, s3));
        SagaModels.SagaContext context = engine.executeSaga(UUID.randomUUID().toString());

        assertEquals("FAILED_REQUIRES_RETRY", context.finalStatus);
        assertFalse(context.isCompensating); // Should not compensate if failed after pivot
        assertTrue(s1.executed && s2.executed && s3.executed);
        assertFalse(s1.compensated || s2.compensated || s3.compensated);
    }

    @Test
    void testOutboxEventDeduplication() {
        TransactionalOutboxRelay relay = new TransactionalOutboxRelay();
        String eventId = UUID.randomUUID().toString();
        
        // Simulating dual writes via local transaction
        relay.insertEvent(new TransactionalOutboxRelay.OutboxEvent(eventId, "Order", "OrderCreated"));
        relay.relayEvents(); // CDC copies to broker
        
        // Simulating duplicate delivery from broker
        relay.insertEvent(new TransactionalOutboxRelay.OutboxEvent(eventId, "Order", "OrderCreated"));
        relay.relayEvents(); // CDC copies to broker again
        
        List<TransactionalOutboxRelay.OutboxEvent> published = relay.getPublishedEvents();
        assertEquals(2, published.size()); // Broker has 2 duplicate messages
        
        InboxConsumer consumer = new InboxConsumer();
        
        boolean firstConsume = consumer.consumeEvent(published.get(0).eventId, published.get(0).payload);
        assertTrue(firstConsume);
        
        boolean secondConsume = consumer.consumeEvent(published.get(1).eventId, published.get(1).payload);
        assertFalse(secondConsume); // Should ignore duplicate
        
        assertEquals(1, consumer.getProcessedItems().size());
        assertEquals("OrderCreated", consumer.getProcessedItems().get(0));
    }
}
