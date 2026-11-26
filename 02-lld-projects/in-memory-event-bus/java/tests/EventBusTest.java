import java.util.ArrayList;
import java.util.List;

public class EventBusTest {

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
    
    private static void assertNull(Object obj) {
        if (obj != null) {
            throw new RuntimeException("Assertion failed: expected null but got " + obj);
        }
    }

    public static void testV2Extended() throws Exception {
        // Test with v2 extended
        InMemoryEventBus bus = new InMemoryEventBus();
        bus.createTopic("test", 2);
        bus.subscribe("g1", "test");
        
        bus.publish("test", "msg1", 0);
        bus.publish("test", "msg2", 1);
        
        assertEquals("msg1", bus.poll("g1", "test", 0));
        assertEquals("msg2", bus.poll("g1", "test", 1));
        
        bus.commitOffset("g1", "test", 0, 1);
        bus.commitOffset("g1", "test", 1, 1);
        System.out.println("testV2Extended passed.");
    }

    public static void testV3Optimized() throws Exception {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("test", 1);
        bus.subscribe("g1", "test");
        
        bus.publish("test", "msg1", 0);
        assertEquals("msg1", bus.poll("g1", "test", 0));
        
        bus.failEvent("g1", "test", "msg1");
        assertEquals("msg1", bus.poll("g1", "test", 0));
        System.out.println("testV3Optimized passed.");
    }

    public static void testV3Dlq() throws Exception {
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("test", 1);
        bus.subscribe("g1", "test");
        
        bus.publish("test", "msg1", 0);
        
        bus.failEvent("g1", "test", "msg1");
        bus.failEvent("g1", "test", "msg1");
        bus.failEvent("g1", "test", "msg1");
        bus.failEvent("g1", "test", "msg1");
        
        assertTrue(bus.getDlq().containsKey("g1_test"));
        assertTrue(bus.getDlq().get("g1_test").contains("msg1"));
        System.out.println("testV3Dlq passed.");
    }

    public static void testV2MultipleGroups() throws Exception {
        InMemoryEventBus bus = new InMemoryEventBus();
        bus.createTopic("test", 1);
        bus.subscribe("g1", "test");
        bus.subscribe("g2", "test");
        
        bus.publish("test", "msg1", 0);
        
        assertEquals("msg1", bus.poll("g1", "test", 0));
        assertEquals("msg1", bus.poll("g2", "test", 0));
        
        bus.commitOffset("g1", "test", 0, 1);
        
        assertNull(bus.poll("g1", "test", 0));
        assertEquals("msg1", bus.poll("g2", "test", 0));
        System.out.println("testV2MultipleGroups passed.");
    }

    public static void testV2ConcurrentPublish() throws Exception {
        // v3 optimized
        v3_optimized.InMemoryEventBus bus = new v3_optimized.InMemoryEventBus();
        bus.createTopic("test", 4);
        
        Thread[] threads = new Thread[4];
        for (int i = 0; i < 4; i++) {
            final int idx = i;
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 100; j++) {
                    bus.publish("test", "msg_" + idx + "_" + j, idx);
                }
            });
            threads[i].start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        for (int i = 0; i < 4; i++) {
            assertEquals(100, bus.getTopics().get("test").getPartitions().get(i).size());
        }
        System.out.println("testV2ConcurrentPublish passed.");
    }

    public static void main(String[] args) throws Exception {
        testV2Extended();
        testV3Optimized();
        testV3Dlq();
        testV2MultipleGroups();
        testV2ConcurrentPublish();
    }
}
