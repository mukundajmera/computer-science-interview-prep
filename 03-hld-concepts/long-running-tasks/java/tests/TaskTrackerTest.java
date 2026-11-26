import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.*;

public class TaskTrackerTest {
    private TaskTracker tracker;

    @BeforeEach
    public void setUp() {
        tracker = new TaskTracker(2);
    }

    @AfterEach
    public void tearDown() {
        tracker.shutdown();
    }

    @Test
    public void testSuccessfulTaskExecutionAndStatus() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<TaskTracker.TaskInfo> callbackInfo = new AtomicReference<>();

        String taskId = tracker.submitTask(context -> {
            context.setProgress(50);
            Thread.sleep(50);
            context.setProgress(100);
            return "Success";
        }, info -> {
            callbackInfo.set(info);
            latch.countDown();
        });

        assertNotNull(taskId);
        TaskTracker.TaskInfo initialInfo = tracker.getTaskInfo(taskId);
        assertNotNull(initialInfo);
        assertTrue(initialInfo.getStatus() == TaskTracker.TaskStatus.QUEUED || initialInfo.getStatus() == TaskTracker.TaskStatus.RUNNING);

        assertTrue(latch.await(2, TimeUnit.SECONDS));

        TaskTracker.TaskInfo finalInfo = tracker.getTaskInfo(taskId);
        assertEquals(TaskTracker.TaskStatus.COMPLETED, finalInfo.getStatus());
        assertEquals(100, finalInfo.getProgress());
        assertEquals("Success", finalInfo.getResult());
        assertNull(finalInfo.getError());

        assertEquals(TaskTracker.TaskStatus.COMPLETED, callbackInfo.get().getStatus());
        assertEquals("Success", callbackInfo.get().getResult());
    }

    @Test
    public void testTaskFailure() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(1);

        String taskId = tracker.submitTask(context -> {
            throw new RuntimeException("Test Exception");
        }, info -> latch.countDown());

        assertTrue(latch.await(2, TimeUnit.SECONDS));

        TaskTracker.TaskInfo finalInfo = tracker.getTaskInfo(taskId);
        assertEquals(TaskTracker.TaskStatus.FAILED, finalInfo.getStatus());
        assertEquals("Test Exception", finalInfo.getError());
        assertNull(finalInfo.getResult());
    }

    @Test
    public void testTaskCancellation() throws InterruptedException {
        CountDownLatch startedLatch = new CountDownLatch(1);
        CountDownLatch finishedLatch = new CountDownLatch(1);

        String taskId = tracker.submitTask(context -> {
            startedLatch.countDown();
            while (!context.isCancelled()) {
                Thread.sleep(10);
            }
            return "Should not return this";
        }, info -> finishedLatch.countDown());

        assertTrue(startedLatch.await(2, TimeUnit.SECONDS)); // Wait for task to start

        TaskTracker.TaskInfo info = tracker.getTaskInfo(taskId);
        assertEquals(TaskTracker.TaskStatus.RUNNING, info.getStatus());

        boolean cancelled = tracker.cancelTask(taskId);
        assertTrue(cancelled);

        assertTrue(finishedLatch.await(2, TimeUnit.SECONDS));

        TaskTracker.TaskInfo finalInfo = tracker.getTaskInfo(taskId);
        assertEquals(TaskTracker.TaskStatus.CANCELLED, finalInfo.getStatus());
    }

    @Test
    public void testCancelNonExistentTask() {
        boolean cancelled = tracker.cancelTask("invalid-id");
        assertFalse(cancelled);
    }
}