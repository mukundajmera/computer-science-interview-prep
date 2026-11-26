import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class JobSchedulerServiceTest {

    private JobSchedulerService scheduler;

    @BeforeEach
    public void setUp() {
        scheduler = new JobSchedulerService();
    }

    @AfterEach
    public void tearDown() {
        scheduler.shutdown();
    }

    @Test
    public void testOneOffJobSuccess() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(1);
        String jobId = scheduler.submitOneOffJob(latch::countDown, 100, 3, 100);

        assertEquals(JobSchedulerService.JobStatus.SCHEDULED, scheduler.getJobStatus(jobId));

        assertTrue(latch.await(2, TimeUnit.SECONDS));

        // Wait a bit to ensure status is updated
        Thread.sleep(100);
        assertEquals(JobSchedulerService.JobStatus.SUCCEEDED, scheduler.getJobStatus(jobId));
    }

    @Test
    public void testPeriodicJobExecution() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3);
        String jobId = scheduler.submitPeriodicJob(latch::countDown, 50, 100, 3, 100);

        assertTrue(latch.await(2, TimeUnit.SECONDS));

        JobSchedulerService.JobStatus status = scheduler.getJobStatus(jobId);
        assertTrue(status == JobSchedulerService.JobStatus.SCHEDULED || status == JobSchedulerService.JobStatus.RUNNING);

        scheduler.cancelJob(jobId);
        assertEquals(JobSchedulerService.JobStatus.CANCELLED, scheduler.getJobStatus(jobId));
    }

    @Test
    public void testJobFailureAndRetryWithBackoff() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3);
        AtomicInteger runCount = new AtomicInteger(0);

        String jobId = scheduler.submitOneOffJob(() -> {
            int current = runCount.incrementAndGet();
            latch.countDown();
            if (current <= 2) {
                throw new RuntimeException("Intentional failure");
            }
        }, 50, 3, 100); // 100ms backoff

        assertTrue(latch.await(3, TimeUnit.SECONDS));

        Thread.sleep(100); // Wait for final status update
        assertEquals(JobSchedulerService.JobStatus.SUCCEEDED, scheduler.getJobStatus(jobId));
        assertEquals(3, runCount.get());
    }

    @Test
    public void testJobExhaustsRetriesAndFails() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(4); // 1 initial + 3 retries

        String jobId = scheduler.submitOneOffJob(() -> {
            latch.countDown();
            throw new RuntimeException("Persistent failure");
        }, 50, 3, 50);

        assertTrue(latch.await(2, TimeUnit.SECONDS));

        Thread.sleep(100); // Wait for state transition
        assertEquals(JobSchedulerService.JobStatus.FAILED, scheduler.getJobStatus(jobId));
    }

    @Test
    public void testCancelJob() throws InterruptedException {
        String jobId = scheduler.submitOneOffJob(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException ignored) {}
        }, 100, 0, 0);

        assertTrue(scheduler.cancelJob(jobId));
        assertEquals(JobSchedulerService.JobStatus.CANCELLED, scheduler.getJobStatus(jobId));
    }
}
