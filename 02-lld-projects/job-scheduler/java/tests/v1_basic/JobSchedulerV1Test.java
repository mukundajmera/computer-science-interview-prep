package v1_basic;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.CopyOnWriteArrayList;

public class JobSchedulerV1Test {
    @Test
    void v1ComponentsExposeStableDescriptions() {
        JobScheduler scheduler = new JobScheduler();
        Job job = new Job();
        JobStore store = new InMemoryJobStore();
        JobExecutor executor = new JobExecutor();

        assertEquals("JobScheduler", scheduler.getId());
        assertEquals("JobScheduler: [store=InMemoryJobStore: 0 jobs, executor=JobExecutor: [running=false, queue_size=0]]", scheduler.describe());
        assertEquals("job", job.getId());
        assertEquals("Job:job [status=CREATED]", job.describe());
        assertEquals("InMemoryJobStore: 0 jobs", ((InMemoryJobStore)store).describe());
        assertEquals("JobExecutor: [running=false, queue_size=0]", executor.describe());
    }

    @Test
    void v1StatusFlowIncludesTerminalStates() {
        assertArrayEquals(
            new JobStatus[] {
                JobStatus.CREATED,
                JobStatus.SCHEDULED,
                JobStatus.RUNNING,
                JobStatus.SUCCEEDED,
                JobStatus.FAILED,
                JobStatus.RETRYING,
                JobStatus.CANCELLED
            },
            JobStatus.values()
        );
    }
    
    @Test
    void testImmediateExecution() throws InterruptedException {
        TestClock clock = new TestClock();
        JobScheduler scheduler = new JobScheduler(new InMemoryJobStore(), clock, 100, 1);
        scheduler.start();
        
        AtomicInteger count = new AtomicInteger(0);
        CountDownLatch latch = new CountDownLatch(1);
        Job job = new Job("job1", () -> {
            count.incrementAndGet();
            latch.countDown();
        }, null, null);
        scheduler.scheduleJob(job);
        
        assertTrue(latch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        
        assertEquals(1, count.get());
        assertEquals(JobStatus.SUCCEEDED, scheduler.getJob("job1").getStatus());
    }
    
    @Test
    void testRetryPolicy() throws InterruptedException {
        TestClock clock = new TestClock();
        JobStore store = new InMemoryJobStore() {
            @Override
            public void saveJob(Job job) {
                super.saveJob(job);
                if (job.getStatus() == JobStatus.RETRYING) {
                    clock.advance(50);
                }
            }
        };
        JobExecutor executor = new JobExecutor(store, clock, 100, 1);
        JobScheduler scheduler = new JobScheduler(store, clock, executor);
        
        AtomicInteger count = new AtomicInteger(0);
        CountDownLatch latch = new CountDownLatch(3);
        Runnable action = () -> {
            count.incrementAndGet();
            latch.countDown();
            throw new RuntimeException("Fail");
        };
        RetryPolicy policy = new RetryPolicy(2, 50, 1.0);
        Job job = new Job("job2", action, null, policy);
        scheduler.scheduleJob(job);
        
        scheduler.start();
        assertTrue(latch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        
        assertEquals(3, count.get());
        assertEquals(JobStatus.FAILED, scheduler.getJob("job2").getStatus());
    }

    @Test
    void testDagDependenciesAndCycles() throws InterruptedException {
        TestClock clock = new TestClock();
        InMemoryJobStore store = new InMemoryJobStore();
        JobScheduler scheduler = new JobScheduler(store, clock, 100, 1);
        scheduler.start();
        
        List<String> results = new CopyOnWriteArrayList<>();
        CountDownLatch latch = new CountDownLatch(3);
        
        Job job1 = new Job("job1", () -> { results.add("job1"); latch.countDown(); }, null, null);
        Job job2 = new Job("job2", () -> { results.add("job2"); latch.countDown(); }, null, null, List.of("job1"));
        Job job3 = new Job("job3", () -> { results.add("job3"); latch.countDown(); }, null, null, List.of("job1", "job2"));

        Job job4 = new Job("job4", () -> {}, null, null, List.of("job5"));
        Job job5 = new Job("job5", () -> {}, null, null, List.of("job4"));
        
        store.saveJob(job5);
        
        assertThrows(IllegalArgumentException.class, () -> scheduler.scheduleJob(job4));

        scheduler.scheduleJob(job1);
        scheduler.scheduleJob(job2);
        scheduler.scheduleJob(job3);

        assertTrue(latch.await(2, TimeUnit.SECONDS));
        scheduler.stop();

        assertEquals(List.of("job1", "job2", "job3"), results);
        assertEquals(JobStatus.SUCCEEDED, scheduler.getJob("job3").getStatus());
    }
    
    @Test
    void testCancellation() throws InterruptedException {
        TestClock clock = new TestClock();
        JobScheduler scheduler = new JobScheduler(new InMemoryJobStore(), clock, 100, 1);
        
        Job job = new Job("job1", () -> {}, null, null);
        job.setNextExecutionTime(clock.now() + 1000);
        scheduler.scheduleJob(job);
        
        assertTrue(scheduler.cancelJob("job1"));
        assertEquals(JobStatus.CANCELLED, scheduler.getJob("job1").getStatus());

        CountDownLatch latch = new CountDownLatch(1);
        Job job2 = new Job("job2", () -> latch.countDown(), null, null);
        job2.setNextExecutionTime(clock.now() + 1000);
        scheduler.scheduleJob(job2);
        
        scheduler.start();
        clock.advance(1000);
        assertTrue(latch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        
        assertEquals(JobStatus.CANCELLED, scheduler.getJob("job1").getStatus());
    }

    @Test
    void testBoundedQueue() {
        TestClock clock = new TestClock();
        JobScheduler scheduler = new JobScheduler(new InMemoryJobStore(), clock, 1, 1);
        
        Job job1 = new Job("job1", () -> {}, null, null);
        job1.setNextExecutionTime(clock.now() + 1000);
        scheduler.scheduleJob(job1);

        Job job2 = new Job("job2", () -> {}, null, null);
        assertThrows(IllegalStateException.class, () -> scheduler.scheduleJob(job2));
    }
    
    @Test
    void testConcurrentPollers() throws InterruptedException {
        TestClock clock = new TestClock();
        JobScheduler scheduler = new JobScheduler(new InMemoryJobStore(), clock, 100, 3);
        scheduler.start();
        
        AtomicInteger count = new AtomicInteger(0);
        CountDownLatch latch = new CountDownLatch(10);
        Runnable action = () -> {
            count.incrementAndGet();
            latch.countDown();
        };

        for (int i = 0; i < 10; i++) {
            scheduler.scheduleJob(new Job("job" + i, action, null, null));
        }

        assertTrue(latch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        assertEquals(10, count.get());
    }

    @Test
    void testMissingDependency() {
        JobScheduler scheduler = new JobScheduler();
        Job job = new Job("job1", () -> {}, null, null, List.of("missing"));
        assertThrows(IllegalArgumentException.class, () -> scheduler.scheduleJob(job));
    }

    @Test
    void testDeterministicDueTimeOrdering() throws InterruptedException {
        TestClock clock = new TestClock();
        JobStore store = new InMemoryJobStore();
        JobExecutor executor = new JobExecutor(store, clock, 100, 1);
        JobScheduler scheduler = new JobScheduler(store, clock, executor);
        
        List<String> results = new CopyOnWriteArrayList<>();
        CountDownLatch latch = new CountDownLatch(2);
        
        Job job2 = new Job("B", () -> { results.add("B"); latch.countDown(); }, null, null);
        job2.setNextExecutionTime(1000);
        Job job1 = new Job("A", () -> { results.add("A"); latch.countDown(); }, null, null);
        job1.setNextExecutionTime(1000);
        
        scheduler.scheduleJob(job2);
        scheduler.scheduleJob(job1);
        
        clock.advance(1000);
        scheduler.start();
        
        assertTrue(latch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        
        assertEquals(List.of("A", "B"), results);
    }

    @Test
    void testFailureDoesNotReleaseDependents() throws InterruptedException {
        TestClock clock = new TestClock();
        JobStore store = new InMemoryJobStore();
        JobExecutor executor = new JobExecutor(store, clock, 100, 1);
        JobScheduler scheduler = new JobScheduler(store, clock, executor);
        
        CountDownLatch failLatch = new CountDownLatch(1);
        CountDownLatch completionLatch = new CountDownLatch(1);
        
        executor.setJobCompletionCallback(j -> {
            if (j.getId().equals("job1") && j.getStatus() == JobStatus.FAILED) {
                completionLatch.countDown();
            }
        });

        Job job1 = new Job("job1", () -> {
            failLatch.countDown();
            throw new RuntimeException("Fail");
        }, null, new RetryPolicy(0, 100, 1.0));
        Job job2 = new Job("job2", () -> {}, null, null, List.of("job1"));
        
        scheduler.scheduleJob(job1);
        scheduler.scheduleJob(job2);
        
        scheduler.start();
        assertTrue(failLatch.await(2, TimeUnit.SECONDS));
        assertTrue(completionLatch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        
        assertEquals(JobStatus.CREATED, scheduler.getJob("job2").getStatus());
    }
    
    @Test
    void testShutdown() throws InterruptedException {
        TestClock clock = new TestClock();
        JobScheduler scheduler = new JobScheduler(new InMemoryJobStore(), clock, 100, 1);
        scheduler.start();
        
        CountDownLatch latch = new CountDownLatch(1);
        CountDownLatch jobRunningLatch = new CountDownLatch(1);
        
        scheduler.scheduleJob(new Job("job1", () -> {
            jobRunningLatch.countDown();
            try {
                latch.await(2, TimeUnit.SECONDS);
            } catch (InterruptedException e) {}
        }, null, null));
        
        assertTrue(jobRunningLatch.await(2, TimeUnit.SECONDS));
        scheduler.stop();
        latch.countDown();
        
        assertTrue(scheduler.describe().contains("running=false"));
    }
}
