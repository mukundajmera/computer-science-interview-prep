package v1_basic;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;

public class DistributedWorkflowTest {

    @Test
    public void testEventHistory() {
        DistributedWorkflow.EventHistory history = new DistributedWorkflow.EventHistory();
        history.addEvent(new DistributedWorkflow.Event(DistributedWorkflow.EventType.WORKFLOW_STARTED, "wf-1"));
        history.addEvent(new DistributedWorkflow.Event(DistributedWorkflow.EventType.ACTIVITY_SCHEDULED, "task-1"));
        
        List<DistributedWorkflow.Event> events = history.replay();
        assertEquals(2, events.size());
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_STARTED, events.get(0).eventType);
        assertEquals(DistributedWorkflow.EventType.ACTIVITY_SCHEDULED, events.get(1).eventType);
    }

    @Test
    public void testActivityExecutorLease() throws InterruptedException {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(100); // 100ms
        executor.submit("task-1", "my_activity");

        assertTrue(executor.acquireLease("task-1"));
        assertFalse(executor.acquireLease("task-1")); // Already leased
        
        assertTrue(executor.heartbeat("task-1"));

        Thread.sleep(150); // wait for lease to expire

        assertFalse(executor.heartbeat("task-1")); // Lease expired
        assertTrue(executor.acquireLease("task-1")); // Re-acquire lease
        assertTrue(executor.complete("task-1", "result"));
    }

    @Test
    public void testSagaCoordinator() {
        DistributedWorkflow.SagaCoordinator saga = new DistributedWorkflow.SagaCoordinator();
        
        List<String> compensated = new ArrayList<>();
        saga.addCompensation(() -> compensated.add("c1"));
        saga.addCompensation(() -> compensated.add("c2"));

        saga.compensate();

        assertEquals(2, compensated.size());
        assertEquals("c2", compensated.get(0));
        assertEquals("c1", compensated.get(1)); // Reverse order
    }

    @Test
    public void testWorkflowOrchestrator() throws Exception {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(5000);
        DistributedWorkflow.WorkflowOrchestrator orchestrator = new DistributedWorkflow.WorkflowOrchestrator(executor);

        orchestrator.startWorkflow("wf-1");
        orchestrator.scheduleActivity("task-1", "act1");

        Thread worker = new Thread(() -> {
            try {
                while (!executor.acquireLease("task-1")) {
                    Thread.sleep(10);
                }
                executor.complete("task-1", "result");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        worker.start();

        Object result = orchestrator.waitForActivity("task-1");
        worker.join();

        assertEquals("result", result);
        orchestrator.completeWorkflow("wf-1");

        List<DistributedWorkflow.Event> events = orchestrator.history.replay();
        assertEquals(4, events.size());
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_COMPLETED, events.get(3).eventType);
    }

    @Test
    public void testWorkflowSagaOnFailure() throws Exception {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(5000);
        DistributedWorkflow.WorkflowOrchestrator orchestrator = new DistributedWorkflow.WorkflowOrchestrator(executor);

        List<String> compensated = new ArrayList<>();

        orchestrator.startWorkflow("wf-1");
        orchestrator.scheduleActivity("task-1", "act1");

        Thread worker1 = new Thread(() -> {
            try {
                while (!executor.acquireLease("task-1")) {
                    Thread.sleep(10);
                }
                executor.complete("task-1", "result1");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        worker1.start();

        orchestrator.waitForActivity("task-1", () -> compensated.add("comp1"));
        worker1.join();

        orchestrator.scheduleActivity("task-2", "act2");

        Thread worker2 = new Thread(() -> {
            try {
                while (!executor.acquireLease("task-2")) {
                    Thread.sleep(10);
                }
                executor.fail("task-2", new Exception("Failed!"));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        worker2.start();

        Exception thrown = assertThrows(Exception.class, () -> {
            orchestrator.waitForActivity("task-2");
        });

        worker2.join();

        orchestrator.failWorkflow("wf-1", new Exception("Workflow failed due to act2"));

        assertEquals(1, compensated.size());
        assertEquals("comp1", compensated.get(0));

        List<DistributedWorkflow.Event> events = orchestrator.history.replay();
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_FAILED, events.get(events.size() - 1).eventType);
    }
}
