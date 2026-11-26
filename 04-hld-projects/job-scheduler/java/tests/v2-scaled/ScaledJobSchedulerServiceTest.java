import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public class ScaledJobSchedulerServiceTest {

    @Test
    public void testJobDependencies() throws InterruptedException {
        ScaledJobSchedulerService scheduler = new ScaledJobSchedulerService();
        List<String> results = new ArrayList<>();

        String job1Id = scheduler.submitOneOffJob(() -> {
            synchronized(results) {
                results.add("task1");
            }
        }, 100, 0, 100);

        String job2Id = scheduler.submitOneOffJob(() -> {
            synchronized(results) {
                results.add("task2");
            }
        }, 0, 0, 100, Arrays.asList(job1Id));

        Thread.sleep(300);

        synchronized(results) {
            assertEquals(2, results.size());
            assertEquals("task1", results.get(0));
            assertEquals("task2", results.get(1));
        }
        assertEquals(ScaledJobSchedulerService.JobStatus.SUCCEEDED, scheduler.getJobStatus(job1Id));
        assertEquals(ScaledJobSchedulerService.JobStatus.SUCCEEDED, scheduler.getJobStatus(job2Id));
        scheduler.shutdown();
    }

    @Test
    public void testDeadLetterQueue() throws InterruptedException {
        ScaledJobSchedulerService scheduler = new ScaledJobSchedulerService();

        String jobId = scheduler.submitOneOffJob(() -> {
            throw new RuntimeException("Failed task");
        }, 0, 2, 50); // 3 attempts

        Thread.sleep(500);

        assertEquals(ScaledJobSchedulerService.JobStatus.DEAD_LETTER, scheduler.getJobStatus(jobId));
        List<String> dlq = scheduler.getDeadLetterQueue();
        assertEquals(1, dlq.size());
        assertEquals(jobId, dlq.get(0));
        scheduler.shutdown();
    }

    @Test
    public void testPauseResume() throws InterruptedException {
        ScaledJobSchedulerService scheduler = new ScaledJobSchedulerService();
        AtomicInteger runs = new AtomicInteger(0);

        String jobId = scheduler.submitOneOffJob(runs::incrementAndGet, 100, 0, 100);

        assertTrue(scheduler.pauseJob(jobId));
        assertEquals(ScaledJobSchedulerService.JobStatus.PAUSED, scheduler.getJobStatus(jobId));

        Thread.sleep(200);
        assertEquals(0, runs.get());

        assertTrue(scheduler.resumeJob(jobId));
        Thread.sleep(200);
        assertEquals(1, runs.get());
        scheduler.shutdown();
    }

    @Test
    public void testWorkerEvictionAndLeaseReassignment() throws InterruptedException {
        ScaledJobSchedulerService scheduler = new ScaledJobSchedulerService(200);
        scheduler.registerWorker("worker1");

        class BlockingTask implements Runnable {
            public boolean started = false;
            public boolean finish = false;
            public int runs = 0;
            public final Object lock = new Object();

            @Override
            public void run() {
                synchronized(lock) {
                    runs++;
                    started = true;
                    lock.notifyAll();
                }
                while (!finish) {
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }

        BlockingTask task = new BlockingTask();
        String jobId = scheduler.submitOneOffJob(task, 0, 1, 10);

        synchronized(task.lock) {
            if (!task.started) {
                task.lock.wait(1000);
            }
        }

        assertTrue(task.started);
        assertEquals(ScaledJobSchedulerService.JobStatus.RUNNING, scheduler.getJobStatus(jobId));

        // Wait for lease to expire
        Thread.sleep(500);

        // The coordinator should detect lease expiry and reassign/retry
        // Wait for it to restart
        Thread.sleep(300);

        synchronized(task.lock) {
            assertTrue(task.runs > 1); // Should have run a second time
        }

        task.finish = true;
        scheduler.shutdown();
    }
}
