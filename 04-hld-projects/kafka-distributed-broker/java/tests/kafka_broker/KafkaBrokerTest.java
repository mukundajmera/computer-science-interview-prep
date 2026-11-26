import kafka_broker.PartitionLog;
import kafka_broker.BrokerCluster;
import kafka_broker.ConsumerGroupCoordinator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class KafkaBrokerTest {

    public static void main(String[] args) {
        System.out.println("Running KafkaBrokerTest...");
        try {
            testPartitionLog();
            testBrokerClusterProduceFetch();
            testBrokerClusterFailover();
            testDeterministicRecovery();
            testConsumerGroupCoordinator();
            testInsufficientIsr();
            testConsumerReplayAndBoundedRetry();
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
}
