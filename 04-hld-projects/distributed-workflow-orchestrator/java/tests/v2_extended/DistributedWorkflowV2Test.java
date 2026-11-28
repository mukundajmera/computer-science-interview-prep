package v2_extended;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;

public class DistributedWorkflowV2Test {

    // ---------- v1 parity: every v1 behavior still holds on the v2 track ----------
    // (acquireLease now returns the task token instead of a boolean, the
    // improvement from FOLLOW-UPS.md #2; the lifecycle being asserted is the same)

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
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(100);
        executor.submit("task-1", "my_activity");

        String token = executor.acquireLease("task-1");
        assertNotNull(token);
        assertNull(executor.acquireLease("task-1")); // Already leased

        assertTrue(executor.heartbeat("task-1", token));

        Thread.sleep(150);

        assertFalse(executor.heartbeat("task-1", token)); // Lease expired
        String newToken = executor.acquireLease("task-1");
        assertNotNull(newToken); // Re-acquire lease
        assertTrue(executor.complete("task-1", newToken, "result"));
    }

    @Test
    public void testSagaCoordinator() {
        DistributedWorkflow.SagaCoordinator saga = new DistributedWorkflow.SagaCoordinator();

        List<String> compensated = new ArrayList<>();
        saga.addCompensation(() -> compensated.add("c1"));
        saga.addCompensation(() -> compensated.add("c2"));

        saga.compensate();

        assertEquals(List.of("c2", "c1"), compensated); // Reverse order
    }

    @Test
    public void testWorkflowOrchestrator() throws Exception {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(5000);
        DistributedWorkflow.WorkflowOrchestrator orchestrator = new DistributedWorkflow.WorkflowOrchestrator(executor);

        orchestrator.startWorkflow("wf-1");
        orchestrator.scheduleActivity("task-1", "act1");

        Thread worker = new Thread(() -> {
            String token = null;
            while (token == null) {
                token = executor.acquireLease("task-1");
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            executor.complete("task-1", token, "result");
        });
        worker.start();

        Object result = orchestrator.waitForActivity("task-1");
        worker.join();

        assertEquals("result", result);
        orchestrator.completeWorkflow("wf-1");

        List<DistributedWorkflow.Event> events = orchestrator.history.replay();
        assertEquals(4, events.size());
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_COMPLETED, events.get(events.size() - 1).eventType);
    }

    @Test
    public void testWorkflowSagaOnFailure() throws Exception {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(5000);
        DistributedWorkflow.WorkflowOrchestrator orchestrator = new DistributedWorkflow.WorkflowOrchestrator(executor);

        List<String> compensated = new ArrayList<>();

        orchestrator.startWorkflow("wf-1");
        orchestrator.scheduleActivity("task-1", "act1");

        Thread worker1 = new Thread(() -> {
            String token = null;
            while (token == null) {
                token = executor.acquireLease("task-1");
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            executor.complete("task-1", token, "result1");
        });
        worker1.start();

        orchestrator.waitForActivity("task-1", () -> compensated.add("comp1"));
        worker1.join();

        orchestrator.scheduleActivity("task-2", "act2");

        Thread worker2 = new Thread(() -> {
            String token = null;
            while (token == null) {
                token = executor.acquireLease("task-2");
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            executor.fail("task-2", token, new Exception("Failed!"));
        });
        worker2.start();

        assertThrows(Exception.class, () -> orchestrator.waitForActivity("task-2"));
        worker2.join();

        orchestrator.failWorkflow("wf-1", new Exception("Workflow failed due to act2"));

        assertEquals(List.of("comp1"), compensated);

        List<DistributedWorkflow.Event> events = orchestrator.history.replay();
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_FAILED, events.get(events.size() - 1).eventType);
    }

    // ---------- v2 improvement 1: task tokens against zombies (FOLLOW-UPS.md #2) ----------

    @Test
    public void testZombieCompletionRejectedAfterReLease() throws InterruptedException {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(100);
        executor.submit("task-1", "act");

        String zombieToken = executor.acquireLease("task-1");
        assertNotNull(zombieToken);

        Thread.sleep(150); // zombie hangs past its lease

        String healthyToken = executor.acquireLease("task-1");
        assertNotNull(healthyToken);
        assertNotEquals(zombieToken, healthyToken);

        // The zombie wakes up and tries to complete: rejected (FOLLOW-UPS.md #2).
        assertFalse(executor.complete("task-1", zombieToken, "stale result"));
        assertTrue(executor.complete("task-1", healthyToken, "fresh result"));
        assertEquals("fresh result", executor.getTask("task-1").result);
    }

    @Test
    public void testZombieFailAndHeartbeatRejectedWithStaleToken() throws InterruptedException {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(100);
        executor.submit("task-1", "act");

        String zombieToken = executor.acquireLease("task-1");
        Thread.sleep(150);
        String healthyToken = executor.acquireLease("task-1");

        assertFalse(executor.heartbeat("task-1", zombieToken));
        assertFalse(executor.fail("task-1", zombieToken, new Exception("stale failure")));
        // The healthy lease is untouched.
        assertTrue(executor.heartbeat("task-1", healthyToken));
    }

    @Test
    public void testCallsWithoutTokenNeverAccepted() {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(5000);
        executor.submit("task-1", "act");
        executor.acquireLease("task-1");

        assertFalse(executor.complete("task-1", null, "result"));
        assertFalse(executor.complete("task-1", "forged-token", "result"));
    }

    // ---------- v2 improvement 2: durable timers (FOLLOW-UPS.md #3/#4) ----------

    @Test
    public void testTimersFireExactlyOnceInOrder() {
        DistributedWorkflow.TimerService service = new DistributedWorkflow.TimerService();
        service.startTimer("timer-2", 1010);
        service.startTimer("timer-1", 1005);

        assertTrue(service.pollExpired(1000).isEmpty());
        assertEquals(List.of("timer-1"), service.pollExpired(1006));
        assertTrue(service.pollExpired(1006).isEmpty()); // already fired, not re-emitted
        assertEquals(List.of("timer-2"), service.pollExpired(1011));
        assertTrue(service.isFired("timer-1"));
        assertTrue(service.isFired("timer-2"));
    }

    @Test
    public void testOrchestratorRecordsTimerEvents() {
        DistributedWorkflow.WorkflowOrchestrator orchestrator =
                new DistributedWorkflow.WorkflowOrchestrator(new DistributedWorkflow.ActivityExecutor(5000));
        orchestrator.startWorkflow("wf-1");
        orchestrator.startTimer("timer-1", 1005);

        List<String> fired = orchestrator.pollTimers(1006);
        assertEquals(List.of("timer-1"), fired);

        List<DistributedWorkflow.Event> events = orchestrator.history.replay();
        assertEquals(3, events.size());
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_STARTED, events.get(0).eventType);
        assertEquals(DistributedWorkflow.EventType.TIMER_STARTED, events.get(1).eventType);
        assertEquals(DistributedWorkflow.EventType.TIMER_FIRED, events.get(2).eventType);
    }

    // ---------- v2 improvement 3: continue-as-new + history limit (FOLLOW-UPS.md #1) ----------

    @Test
    public void testContinueAsNewResetsHistoryAndCarriesState() {
        DistributedWorkflow.WorkflowOrchestrator orchestrator =
                new DistributedWorkflow.WorkflowOrchestrator(new DistributedWorkflow.ActivityExecutor(5000));
        orchestrator.startWorkflow("wf-cron");
        orchestrator.scheduleActivity("task-1", "act1");
        orchestrator.scheduleActivity("task-2", "act2");

        List<String> state = List.of("task-1", "task-2");
        DistributedWorkflow.WorkflowOrchestrator newRun = orchestrator.continueAsNew("wf-cron", state);

        assertEquals("CONTINUED_AS_NEW", orchestrator.workflowStatus);
        List<DistributedWorkflow.Event> oldEvents = orchestrator.history.replay();
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_CONTINUED_AS_NEW,
                oldEvents.get(oldEvents.size() - 1).eventType);
        assertEquals(state, oldEvents.get(oldEvents.size() - 1).payload);

        assertEquals(orchestrator.runId + 1, newRun.runId);
        assertEquals(state, newRun.carriedState);
        List<DistributedWorkflow.Event> newEvents = newRun.history.replay();
        assertEquals(1, newEvents.size()); // empty history, just the new start
        assertEquals(DistributedWorkflow.EventType.WORKFLOW_STARTED, newEvents.get(0).eventType);
    }

    @Test
    public void testHistoryLimitEnforced() {
        DistributedWorkflow.WorkflowOrchestrator orchestrator = new DistributedWorkflow.WorkflowOrchestrator(
                new DistributedWorkflow.ActivityExecutor(5000), new DistributedWorkflow.TimerService(), 3, 1, null);
        orchestrator.startWorkflow("wf-1");       // event 1
        orchestrator.scheduleActivity("t1", "a");  // event 2
        orchestrator.scheduleActivity("t2", "b");  // event 3

        assertThrows(IllegalStateException.class, () -> orchestrator.scheduleActivity("t3", "c"));
    }

    @Test
    public void testNewRunContinuesWorkingAfterContinueAsNew() throws Exception {
        DistributedWorkflow.ActivityExecutor executor = new DistributedWorkflow.ActivityExecutor(5000);
        DistributedWorkflow.WorkflowOrchestrator orchestrator = new DistributedWorkflow.WorkflowOrchestrator(
                executor, new DistributedWorkflow.TimerService(), 2, 1, null);
        orchestrator.startWorkflow("wf-cron");      // event 1
        orchestrator.scheduleActivity("t1", "a");    // event 2, limit reached

        DistributedWorkflow.WorkflowOrchestrator newRun = orchestrator.continueAsNew("wf-cron", "done:t1");

        // The fresh run has room to schedule again and completes end to end.
        newRun.scheduleActivity("t2", "b");

        Thread worker = new Thread(() -> {
            String token = null;
            while (token == null) {
                token = executor.acquireLease("t2");
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            executor.complete("t2", token, "result2");
        });
        worker.start();
        assertEquals("result2", newRun.waitForActivity("t2"));
        worker.join();

        newRun.completeWorkflow("wf-cron");
        assertEquals("COMPLETED", newRun.workflowStatus);
    }
}
