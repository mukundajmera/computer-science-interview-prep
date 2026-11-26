package v1_basic;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MultiPolicyCacheTest {
    @Test
    public void testLruEviction() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LRU);
        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        cache.get("A"); // A is accessed
        cache.put("D", "4"); // B should be evicted
        
        assertNull(cache.get("B"));
        assertEquals("1", cache.get("A"));
        assertEquals("3", cache.get("C"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }

    @Test
    public void testFifoEviction() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.FIFO);
        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        cache.get("A"); // A is accessed, but FIFO doesn't care
        cache.put("D", "4"); // A should be evicted because it's oldest
        
        assertNull(cache.get("A"));
        assertEquals("2", cache.get("B"));
        cache.shutdown();
    }

    @Test
    public void testLfuEviction() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LFU);
        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        cache.get("A"); // freq 2
        cache.get("A"); // freq 3
        cache.get("B"); // freq 2
        cache.put("D", "4"); // C should be evicted (freq 1)
        
        assertNull(cache.get("C"));
        assertEquals("1", cache.get("A"));
        assertEquals("2", cache.get("B"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }

    @Test
    public void testPolicySwap() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.FIFO);
        cache.put("A", "1");
        try { Thread.sleep(10); } catch(Exception e) {}
        cache.put("B", "2");
        try { Thread.sleep(10); } catch(Exception e) {}
        cache.put("C", "3");
        
        cache.get("A"); // A accessed
        
        cache.changePolicy(EvictionPolicy.LRU);
        // Now it's LRU. A is most recently accessed. C was inserted last.
        // B was least recently accessed.
        cache.put("D", "4"); // B should be evicted.
        
        assertNull(cache.get("B"));
        assertEquals("1", cache.get("A"));
        assertEquals("3", cache.get("C"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }

    @Test
    public void testTtlExpiration() throws InterruptedException {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LRU);
        cache.put("A", "1", 100); // 100ms TTL
        cache.put("B", "2"); // No TTL
        
        Thread.sleep(200); // Wait for TTL
        
        assertNull(cache.get("A")); // Passive eviction
        assertEquals("2", cache.get("B"));
        cache.shutdown();
    }
    
    @Test
    public void testActiveExpiration() throws InterruptedException {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LRU);
        cache.put("A", "1", 100);
        
        assertEquals(1, cache.size());
        Thread.sleep(1500); // Wait for cleanup thread
        
        assertEquals(0, cache.size()); // Active eviction
        cache.shutdown();
    }
}
