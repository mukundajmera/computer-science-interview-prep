package v3_distributed;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class DistributedJobSchedulerTest {

    private DistributedJobScheduler.Datastore datastore;

    @BeforeEach
    public void setup() {
        datastore = new DistributedJobScheduler.Datastore();
    }

    private DistributedJobScheduler.JobHandler createMockHandler(Set<String> executedJobs) {
        return (jobId, token) -> {
            executedJobs.add(jobId);
            return true;
        };
    }

    private DistributedJobScheduler.JobHandler createFailHandler() {
        return (jobId, token) -> false;
    }

    @Test
    public void testBasicSchedulingAndExecution() {
        Set<String> executed = new HashSet<>();
        DistributedJobScheduler node1 = new DistributedJobScheduler("node-1", datastore, createMockHandler(executed));

        datastore.submitJob("job-1", 1000);

        node1.tick(500);
        assertTrue(node1.isLeader());
        assertEquals(DistributedJobScheduler.JobState.SCHEDULED, datastore.getJob("job-1").state);

        node1.tick(1000);
        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-1").state);
        assertTrue(executed.contains("job-1"));
        assertEquals(1, datastore.getJob("job-1").attempt);
    }

    @Test
    public void testConsistentHashingAssignment() {
        Set<String> executed1 = new HashSet<>();
        Set<String> executed2 = new HashSet<>();
        DistributedJobScheduler node1 = new DistributedJobScheduler("node-1", datastore, createMockHandler(executed1));
        DistributedJobScheduler node2 = new DistributedJobScheduler("node-2", datastore, createMockHandler(executed2));

        datastore.submitJob("job-1", 1000);
        datastore.submitJob("job-2", 1000);
        datastore.submitJob("job-3", 1000);
        datastore.submitJob("job-4", 1000);

        node1.tick(500);
        node2.tick(500);

        node1.tick(1000);
        node2.tick(1000);

        assertTrue(node1.isLeader() || node2.isLeader());

        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-1").state);
        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-2").state);
        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-3").state);
        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-4").state);

        assertEquals(4, executed1.size() + executed2.size());
    }

    @Test
    public void testWorkerFailover() {
        Set<String> executed1 = new HashSet<>();
        Set<String> executed2 = new HashSet<>();
        DistributedJobScheduler node1 = new DistributedJobScheduler("node-1", datastore, createFailHandler());
        DistributedJobScheduler node2 = new DistributedJobScheduler("node-2", datastore, createMockHandler(executed2));

        datastore.submitJob("job-1", 1000);

        node1.tick(1000);
        assertEquals(DistributedJobScheduler.JobState.FAILED, datastore.getJob("job-1").state);

        node2.tick(1500);
        node1.tick(1500);

        node2.tick(2000);
        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-1").state);
    }

    @Test
    public void testIdempotencyToken() {
        Set<String> executed = new HashSet<>();
        int[] executionCount = {0};

        DistributedJobScheduler.JobHandler idempotentHandler = (jobId, token) -> {
            executionCount[0]++;
            return true;
        };

        DistributedJobScheduler node1 = new DistributedJobScheduler("node-1", datastore, idempotentHandler);

        datastore.submitJob("job-1", 1000);

        node1.tick(1000);
        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-1").state);
        assertEquals(1, executionCount[0]);

        synchronized (datastore) {
            datastore.getJob("job-1").state = DistributedJobScheduler.JobState.RUNNING;
            datastore.getJob("job-1").leaseUntil = 3000;
        }

        node1.tick(2000);

        assertEquals(DistributedJobScheduler.JobState.COMPLETED, datastore.getJob("job-1").state);
        assertEquals(1, executionCount[0]);
    }

    @Test
    public void testLeaderElection() {
        DistributedJobScheduler node1 = new DistributedJobScheduler("node-1", datastore, createMockHandler(new HashSet<>()));
        DistributedJobScheduler node2 = new DistributedJobScheduler("node-2", datastore, createMockHandler(new HashSet<>()));

        node1.tick(100);
        assertTrue(node1.isLeader());

        node2.tick(200);
        assertFalse(node2.isLeader());

        node2.tick(5500);
        assertTrue(node2.isLeader());

        node1.tick(5600);
        assertFalse(node1.isLeader());
    }

    @Test
    public void testDeadLetter() {
        DistributedJobScheduler node1 = new DistributedJobScheduler("node-1", datastore, createFailHandler());

        datastore.submitJob("job-1", 1000);

        node1.tick(1000);
        node1.tick(2000);
        node1.tick(3000);
        node1.tick(4000);

        assertEquals(DistributedJobScheduler.JobState.DEAD_LETTER, datastore.getJob("job-1").state);
        assertEquals(4, datastore.getJob("job-1").attempt);
    }
}
