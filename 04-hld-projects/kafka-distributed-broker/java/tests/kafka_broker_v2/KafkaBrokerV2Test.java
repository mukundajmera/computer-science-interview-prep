import kafka_broker_v2.PartitionLog;
import kafka_broker_v2.BrokerCluster;
import kafka_broker_v2.ConsumerGroupCoordinator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class KafkaBrokerV2Test {

    public static void main(String[] args) {
        System.out.println("Running KafkaBrokerV2Test...");
        try {
            testPartitionLog();
            testBrokerClusterProduceFetch();
            testBrokerClusterFailover();
            testDeterministicRecovery();
            testConsumerGroupCoordinator();
            testInsufficientIsr();
            testConsumerReplayAndBoundedRetry();
            testRetentionDeletesInactiveSegments();
            testRetentionDeletesByAge();
            testRetentionNeverDeletesActiveSegment();
            testDiskUsageBytes();
            testIdempotentProduceDedupesRetry();
            testIdempotentProduceRejectsGap();
            testIdempotentProducePerPartition();
            testInjectableClockHealthCheck();
            testConsumerLagMetric();
            System.out.println("All tests passed.");
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void assertEqual(int expected, int actual) {
        if (expected != actual) {
            throw new RuntimeException("Expected " + expected + " but got " + actual);
        }
    }

    private static void assertEqual(long expected, long actual, String label) {
        if (expected != actual) {
            throw new RuntimeException(label + ": expected " + expected + " but got " + actual);
        }
    }

    private static void assertEqual(String expected, String actual) {
        if (!expected.equals(actual)) {
            throw new RuntimeException("Expected " + expected + " but got " + actual);
        }
    }

    private static void assertTrue(boolean condition) {
        if (!condition) {
            throw new RuntimeException("Expected condition to be true");
        }
    }

    private static void testPartitionLog() {
        PartitionLog log = new PartitionLog(50);
        byte[] msg1 = "Hello Kafka 1".getBytes();
        byte[] msg2 = "Hello Kafka 2".getBytes();
        byte[] msg3 = "Hello Kafka 3".getBytes();
        byte[] msg4 = "Hello Kafka 4".getBytes();

        int offset1 = log.append(msg1);
        int offset2 = log.append(msg2);
        int offset3 = log.append(msg3);
        int offset4 = log.append(msg4);

        assertEqual(0, offset1);
        assertEqual(1, offset2);
        assertEqual(2, offset3);
        assertEqual(3, offset4);

        List<PartitionLog.Message> msgs = log.read(1, 2);
        assertEqual(2, msgs.size());
        assertEqual("Hello Kafka 2", new String(msgs.get(0).data));
        assertEqual("Hello Kafka 3", new String(msgs.get(1).data));

        assertEqual(4, log.getLogEndOffset());
        
        log.truncateTo(3);
        assertEqual(3, log.getLogEndOffset());
        
        // Simulating retention gap
        log.truncateTo(5); // This will clear all segments since we truncated to 5. Actually no wait, truncateTo is from tail.
        // We can't directly pop segments since it's private. But we can test invalid offset.
        boolean threw = false;
        try {
            log.read(6, 10);
        } catch (IllegalArgumentException e) {
            threw = true;
        }
        assertTrue(threw);
    }

    private static void testBrokerClusterProduceFetch() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");

        cluster.produce("p1", "msg1".getBytes(), 1);
        cluster.produce("p1", "msg2".getBytes(), -1);

        List<byte[]> msgs = cluster.fetch("p1", 0, 10);
        assertEqual(2, msgs.size());
        assertEqual("msg1", new String(msgs.get(0)));
        assertEqual("msg2", new String(msgs.get(1)));
    }

    private static void testDeterministicRecovery() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");

        cluster.produce("p1", "msg1".getBytes(), 1);
        cluster.failBroker("broker1");

        cluster.produce("p1", "msg2".getBytes(), -1);

        cluster.recoverBroker("broker1");

        List<byte[]> msgs = cluster.fetch("p1", 0, 10);
        assertEqual(1, msgs.size());
        assertEqual("msg2", new String(msgs.get(0)));
    }

    private static void testInsufficientIsr() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");
        
        cluster.failBroker("broker2");
        cluster.failBroker("broker3");
        
        boolean threw = false;
        try {
            cluster.produce("p1", "msg1".getBytes(), -1);
        } catch (RuntimeException e) {
            if (e.getMessage() != null && e.getMessage().contains("Insufficient ISR")) {
                threw = true;
            }
        }
        assertTrue(threw);
    }

    private static void testBrokerClusterFailover() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");

        cluster.produce("p1", "msg1".getBytes(), -1);

        cluster.failBroker("broker1");

        // Can still produce? New leader should be elected.
        cluster.produce("p1", "msg2".getBytes(), -1);

        List<byte[]> msgs = cluster.fetch("p1", 0, 10);
        assertEqual(2, msgs.size());
        assertEqual("msg1", new String(msgs.get(0)));
        assertEqual("msg2", new String(msgs.get(1)));
    }

    private static void testConsumerGroupCoordinator() throws InterruptedException {
        ConsumerGroupCoordinator coordinator = new ConsumerGroupCoordinator(100);
        coordinator.registerGroup("g1", Arrays.asList("p1", "p2", "p3"));

        coordinator.joinGroup("g1", "c1");
        coordinator.joinGroup("g1", "c2");

        List<String> c1Assignment = coordinator.getAssignment("g1", "c1");
        List<String> c2Assignment = coordinator.getAssignment("g1", "c2");

        assertEqual(3, c1Assignment.size() + c2Assignment.size());

        Thread.sleep(200);
        coordinator.heartbeat("g1", "c1");
        coordinator.checkHealth();

        List<String> c1AssignmentNew = coordinator.getAssignment("g1", "c1");
        assertEqual(3, c1AssignmentNew.size());
    }

    private static void testConsumerReplayAndBoundedRetry() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");

        cluster.produce("p1", "msg1".getBytes(), -1);
        cluster.produce("p1", "msg2".getBytes(), -1);
        cluster.produce("p1", "msg3".getBytes(), -1);

        ConsumerGroupCoordinator coordinator = new ConsumerGroupCoordinator(100);
        coordinator.registerGroup("g1", Arrays.asList("p1"));
        coordinator.joinGroup("g1", "c1");

        // 1. Group progression (successful fetch and commit)
        int fetchOffset = coordinator.fetchOffset("g1", "p1");
        assertEqual(0, fetchOffset);

        List<byte[]> msgs = cluster.fetch("p1", fetchOffset, 1);
        assertEqual(1, msgs.size());
        assertEqual("msg1", new String(msgs.get(0)));

        coordinator.commitOffset("g1", "p1", fetchOffset + msgs.size());

        // 2. Duplicate replay (crashing before commit, refetching, and processing duplicates)
        // Fetch msg2 and msg3
        fetchOffset = coordinator.fetchOffset("g1", "p1");
        assertEqual(1, fetchOffset);
        
        msgs = cluster.fetch("p1", fetchOffset, 2);
        assertEqual(2, msgs.size());
        assertEqual("msg2", new String(msgs.get(0)));
        assertEqual("msg3", new String(msgs.get(1)));

        // Simulating crash before commit: we DO NOT call commitOffset.
        
        // Re-fetch due to crash (duplicate replay)
        int refetchOffset = coordinator.fetchOffset("g1", "p1");
        assertEqual(1, refetchOffset); // Still 1 since we didn't commit

        List<byte[]> duplicateMsgs = cluster.fetch("p1", refetchOffset, 2);
        assertEqual(2, duplicateMsgs.size());
        assertEqual("msg2", new String(duplicateMsgs.get(0)));
        assertEqual("msg3", new String(duplicateMsgs.get(1)));

        // Now commit successfully
        coordinator.commitOffset("g1", "p1", refetchOffset + duplicateMsgs.size());

        // 3. Bounded shutdown (finite retry loops to avoid hangs)
        // Simulate checking for new messages with bounded retries
        int retryCount = 0;
        int maxRetries = 3;
        List<byte[]> finalMsgs = new ArrayList<>();
        
        while (retryCount < maxRetries) {
            int currentOffset = coordinator.fetchOffset("g1", "p1");
            finalMsgs = cluster.fetch("p1", currentOffset, 10);
            if (!finalMsgs.isEmpty()) {
                break;
            }
            retryCount++;
            // Normally would sleep or backoff here
        }
        
        assertEqual(maxRetries, retryCount); // Should exhaust retries as no new messages are produced
        assertEqual(0, finalMsgs.size());
    }
    // --- v2-only tests: improvements 1-3 ---

    private static void testRetentionDeletesInactiveSegments() {
        PartitionLog log = new PartitionLog(20); // 20-byte segments
        for (int i = 0; i < 5; i++) {
            log.append("aaaaa".getBytes()); // 5 bytes each; 5th rolls a new segment
        }
        // segment 0: offsets 0-3 (20 bytes), segment 1 (active): offset 4 (5 bytes)
        assertEqual(25, log.diskUsageBytes(), "usage before retention");
        int deleted = log.enforceRetention(10L, null);
        assertEqual(1, deleted, "only the inactive head segment is deleted");
        assertEqual(5, log.diskUsageBytes(), "usage after retention");
        try {
            log.read(0, 1);
            throw new RuntimeException("expected OffsetOutOfRange after retention");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("OffsetOutOfRange"));
        }
        System.out.println("testRetentionDeletesInactiveSegments passed.");
    }

    private static void testRetentionDeletesByAge() {
        final long[] now = {1000L};
        PartitionLog log = new PartitionLog(20, () -> now[0]);
        for (int i = 0; i < 5; i++) {
            log.append("aaaaa".getBytes());
        }
        now[0] = 1200L; // both segments are 200ms old
        int deleted = log.enforceRetention(null, 100L);
        assertEqual(1, deleted, "aged inactive segment deleted, active one kept");
        assertEqual(5, log.diskUsageBytes(), "active segment survives age policy");
        System.out.println("testRetentionDeletesByAge passed.");
    }

    private static void testRetentionNeverDeletesActiveSegment() {
        PartitionLog log = new PartitionLog(100);
        log.append("aaaaa".getBytes());
        int deleted = log.enforceRetention(0L, null);
        assertEqual(0, deleted, "active segment kept even over cap");
        assertEqual(5, log.diskUsageBytes(), "active bytes retained");
        System.out.println("testRetentionNeverDeletesActiveSegment passed.");
    }

    private static void testDiskUsageBytes() {
        PartitionLog log = new PartitionLog(20);
        assertEqual(0, log.diskUsageBytes(), "empty log uses 0 bytes");
        log.append("abc".getBytes());
        log.append("de".getBytes());
        assertEqual(5, log.diskUsageBytes(), "usage sums appended bytes");
        System.out.println("testDiskUsageBytes passed.");
    }

    private static void testIdempotentProduceDedupesRetry() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");
        int o1 = cluster.produceIdempotent("p1", "x".getBytes(), -1, "prod-1", 0);
        int o2 = cluster.produceIdempotent("p1", "x".getBytes(), -1, "prod-1", 0);
        assertEqual(o1, o2, "retry returns the original offset");
        assertEqual(1, cluster.fetch("p1", 0, 10).size(), "no duplicate appended");
        System.out.println("testIdempotentProduceDedupesRetry passed.");
    }

    private static void testIdempotentProduceRejectsGap() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");
        cluster.produceIdempotent("p1", "x".getBytes(), -1, "prod-1", 0);
        try {
            cluster.produceIdempotent("p1", "y".getBytes(), -1, "prod-1", 5);
            throw new RuntimeException("expected OutOfOrderSequence");
        } catch (IllegalStateException e) {
            assertTrue(e.getMessage().contains("OutOfOrderSequence"));
        }
        assertEqual(1, cluster.fetch("p1", 0, 10).size(), "rejected gap appended nothing");
        System.out.println("testIdempotentProduceRejectsGap passed.");
    }

    private static void testIdempotentProducePerPartition() {
        BrokerCluster cluster = new BrokerCluster(Arrays.asList("broker1", "broker2", "broker3"));
        cluster.createPartition("p1", Arrays.asList("broker1", "broker2", "broker3"), "broker1");
        cluster.createPartition("p2", Arrays.asList("broker1", "broker2", "broker3"), "broker1");
        cluster.produceIdempotent("p1", "x".getBytes(), -1, "prod-1", 0);
        cluster.produceIdempotent("p2", "y".getBytes(), -1, "prod-1", 0); // same sequence, other partition
        assertEqual(1, cluster.fetch("p2", 0, 10).size(), "sequences are tracked per partition");
        System.out.println("testIdempotentProducePerPartition passed.");
    }

    private static void testInjectableClockHealthCheck() {
        final long[] now = {1000L};
        ConsumerGroupCoordinator coord = new ConsumerGroupCoordinator(100, () -> now[0]);
        java.util.List<String> parts = java.util.Arrays.asList("p1");
        coord.registerGroup("g1", parts);
        coord.joinGroup("g1", "m1");
        now[0] = 1080L; // 80ms since join, inside the 100ms timeout
        coord.checkHealth();
        assertEqual("p1", coord.getAssignment("g1", "m1").get(0)); // member alive inside timeout
        now[0] = 1201L; // 201ms since join, past the timeout
        coord.checkHealth();
        assertTrue(coord.getAssignment("g1", "m1").isEmpty()); // member evicted past timeout
        System.out.println("testInjectableClockHealthCheck passed.");
    }

    private static void testConsumerLagMetric() {
        ConsumerGroupCoordinator coord = new ConsumerGroupCoordinator(5000);
        coord.registerGroup("g1", java.util.Arrays.asList("p1"));
        coord.commitOffset("g1", "p1", 3);
        assertEqual(7, coord.consumerLag("g1", "p1", 10), "lag is log end minus committed");
        System.out.println("testConsumerLagMetric passed.");
    }
}
