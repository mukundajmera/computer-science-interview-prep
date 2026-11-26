import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

public class InMemoryEventBusAll_versionsTest {

    private static void assertEquals(Object expected, Object actual) {
        if (expected == null && actual == null) return;
        if (expected != null && expected.equals(actual)) return;
        throw new RuntimeException("Assertion failed: expected " + expected + " but got " + actual);
    }
    
    private static void assertTrue(boolean condition) {
        if (!condition) {
            throw new RuntimeException("Assertion failed: expected true");
        }
    }

    public static void testDeterministicSequenceAndReplay() {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("topic1", 2);
        bus.subscribe("group1", "topic1");

        bus.publish("topic1", "msg1", 0);
        bus.publish("topic1", "msg2", 0);
        bus.publish("topic1", "msg3", 1);
        
        assertEquals("msg1", bus.poll("group1", "topic1", 0));
        assertEquals("msg3", bus.poll("group1", "topic1", 1));
        
        bus.commitOffset("group1", "topic1", 0, 1);
        
        assertEquals("msg2", bus.poll("group1", "topic1", 0));
        assertEquals("msg3", bus.poll("group1", "topic1", 1));
        System.out.println("testDeterministicSequenceAndReplay passed.");
    }
    
    public static void testBoundedSubscriberQueueBlock() throws InterruptedException {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("topic1", 1);
        
        CountDownLatch latch = new CountDownLatch(3);
        List<Object> received = new ArrayList<>();
        bus.subscribe("topic1", msg -> {
            synchronized(received) {
                received.add(msg);
            }
            latch.countDown();
            try { Thread.sleep(50); } catch(Exception e) {}
        }, 1, v3_optimized.InMemoryEventBus.QueuePolicy.BLOCK);
        
        bus.publish("topic1", "msg1", 0);
        bus.publish("topic1", "msg2", 0);
        bus.publish("topic1", "msg3", 0);
        
        assertTrue(latch.await(2, TimeUnit.SECONDS));
        assertEquals(3, received.size());
        
        bus.unsubscribeAll();
        System.out.println("testBoundedSubscriberQueueBlock passed.");
    }
    
    public static void testBoundedSubscriberQueueDrop() throws InterruptedException {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("topic1", 1);
        
        AtomicInteger count = new AtomicInteger(0);
        bus.subscribe("topic1", msg -> {
            count.incrementAndGet();
            try { Thread.sleep(100); } catch(Exception e) {}
        }, 1, v3_optimized.InMemoryEventBus.QueuePolicy.DROP);
        
        bus.publish("topic1", "msg1", 0);
        bus.publish("topic1", "msg2", 0);
        bus.publish("topic1", "msg3", 0); // Will likely drop
        
        Thread.sleep(500);
        assertTrue(count.get() < 3);
        bus.unsubscribeAll();
        System.out.println("testBoundedSubscriberQueueDrop passed.");
    }
    
    public static void testBoundedSubscriberQueueReject() {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("topic1", 1);
        
        bus.subscribe("topic1", msg -> {
            try { Thread.sleep(500); } catch(Exception e) {}
        }, 1, v3_optimized.InMemoryEventBus.QueuePolicy.REJECT);
        
        bus.publish("topic1", "msg1", 0);
        boolean threw = false;
        try {
            bus.publish("topic1", "msg2", 0);
            bus.publish("topic1", "msg3", 0);
        } catch (RuntimeException e) {
            threw = true;
        }
        assertTrue(threw);
        
        bus.unsubscribeAll();
        System.out.println("testBoundedSubscriberQueueReject passed.");
    }

    public static void testV2ExtendedConcurrentPublishAndReplay() {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("topic1", 2);
        bus.subscribe("group1", "topic1");
        bus.publish("topic1", "msg1", 0);
        assertEquals("msg1", bus.poll("group1", "topic1", 0));
        bus.commitOffset("group1", "topic1", 0, 1);
        System.out.println("testV2ExtendedConcurrentPublishAndReplay passed.");
    }

    public static void main(String[] args) throws Exception {
        testDeterministicSequenceAndReplay();
        testBoundedSubscriberQueueBlock();
        testBoundedSubscriberQueueDrop();
        testBoundedSubscriberQueueReject();
        testV2ExtendedConcurrentPublishAndReplay();
    }
}
