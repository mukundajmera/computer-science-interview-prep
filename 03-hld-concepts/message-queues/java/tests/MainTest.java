import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Comparator;
import java.util.List;

public class MainTest {
    public static void main(String[] args) throws Exception {
        System.out.println("Running SimpleQueue tests...");
        testSimpleQueue();
        
        System.out.println("Running PubSubQueue tests...");
        testPubSubQueue();
        
        System.out.println("Running DurableQueue tests...");
        testDurableQueue();
        
        System.out.println("All tests passed!");
    }

    private static void testSimpleQueue() throws InterruptedException {
        SimpleQueue<String> q = new SimpleQueue<>(2);
        
        assert q.isEmpty() : "Queue should be empty";
        assert q.enqueue("A", 100) : "Enqueue A failed";
        assert q.enqueue("B", 100) : "Enqueue B failed";
        assert q.isFull() : "Queue should be full";
        
        // Backpressure test
        assert !q.enqueue("C", 10) : "Enqueue C should have timed out";
        
        assert "A".equals(q.dequeue(100)) : "Dequeue should be A";
        assert q.size() == 1 : "Size should be 1";
        
        q.clear();
        assert q.isEmpty() : "Queue should be empty after clear";
    }

    private static void testPubSubQueue() throws InterruptedException {
        PubSubQueue<String> q = new PubSubQueue<>();
        q.subscribe("logs", "group1", 100, 2); // 100ms visibility, max 2 deliveries
        
        q.publish("logs", "error1");
        
        PubSubQueue.Message<String> msg1 = q.pull("logs", "group1");
        assert msg1 != null : "Should pull msg1";
        assert "error1".equals(msg1.payload) : "Payload should be error1";
        
        // Visibility timeout test
        PubSubQueue.Message<String> msgEmpty = q.pull("logs", "group1");
        assert msgEmpty == null : "Should be empty because of in-flight";
        
        Thread.sleep(150); // wait for visibility timeout
        
        // 2nd delivery -> maxDeliveries is 2, so it will go straight to DLQ and return null
        PubSubQueue.Message<String> msg2 = q.pull("logs", "group1");
        assert msg2 == null : "Should pull redelivered message but max deliveries reached and sent to DLQ";
        
        // Dead letter queue test
        
        List<PubSubQueue.Message<String>> dlq = q.getDlq("logs", "group1");
        assert dlq.size() == 1 : "DLQ should have 1 message";
        assert dlq.get(0).payload.equals("error1") : "DLQ payload mismatch";
    }

    private static void testDurableQueue() throws Exception {
        File tempDir = Files.createTempDirectory("durable_queue_tests").toFile();
        try {
            DurableQueue q = new DurableQueue(tempDir.getAbsolutePath(), 4);
            
            // Produce
            long[] info = q.produce("user_id_123", "signup_event");
            int partId = (int) info[0];
            long offset = info[1];
            
            // Consume
            DurableQueue.DurableMessage msg = q.consume("groupA", partId);
            assert msg != null : "Should consume a message";
            assert "signup_event".equals(msg.payload) : "Payload should match";
            assert msg.offset == offset : "Offset should match";
            
            // Commit
            q.commitOffset("groupA", partId, offset + 1);
            
            // Consume again should be null
            DurableQueue.DurableMessage msg2 = q.consume("groupA", partId);
            assert msg2 == null : "Should be null after commit";
            
            // Test Idempotent Consumer
            q.produce("key1", "process_me");
            DurableQueue.IdempotentConsumer consumer = new DurableQueue.IdempotentConsumer(q, "group_idem", 2);
            
            // First time fails
            boolean success = consumer.consumeAndProcess(partId, payload -> {
                throw new RuntimeException("Transient failure");
            });
            assert !success : "Should fail";
            
            // Still in queue (offset not committed)
            // Second time fails -> goes to DLQ
            success = consumer.consumeAndProcess(partId, payload -> {
                throw new RuntimeException("Transient failure again");
            });
            assert !success : "Should fail again";
            
            assert consumer.getDlq().size() == 1 : "Should be 1 in DLQ";
            
        } finally {
            // Cleanup
            Files.walk(tempDir.toPath())
                .sorted(Comparator.reverseOrder())
                .map(java.nio.file.Path::toFile)
                .forEach(File::delete);
        }
    }
}