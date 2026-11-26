package v2_extended;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MultiPolicyCacheV2Test {
    @Test
    public void testV2LfuTieBreaking() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LFU);
        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        
        // A, B, C all have freq=1. LRU order: A is LRU, C is MRU.
        // D should evict A.
        cache.put("D", "4");
        assertNull(cache.get("A"));
        assertEquals("2", cache.get("B"));
        assertEquals("3", cache.get("C"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }

    @Test
    public void testV2LfuFrequencyIncrements() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LFU);
        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        
        cache.get("A"); // freq 2
        cache.get("A"); // freq 3
        cache.get("B"); // freq 2
        
        // C is freq 1, A is 3, B is 2
        cache.put("D", "4"); // Evicts C
        assertNull(cache.get("C"));
        assertEquals("1", cache.get("A"));
        assertEquals("2", cache.get("B"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }

    @Test
    public void testV2PolicyHotSwapping() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.FIFO);
        cache.put("A", "1");
        try { Thread.sleep(10); } catch(Exception e) {}
        cache.put("B", "2");
        try { Thread.sleep(10); } catch(Exception e) {}
        cache.put("C", "3");
        
        cache.get("A"); // Access A
        
        // Swap to LRU
        cache.changePolicy(EvictionPolicy.LRU);
        cache.put("D", "4"); // Evicts B (least recently accessed)
        
        assertNull(cache.get("B"));
        assertEquals("1", cache.get("A"));
        assertEquals("3", cache.get("C"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }

    @Test
    public void testV2LfuPolicyHotSwapping() {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(3, EvictionPolicy.LRU);
        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        
        cache.get("A");
        cache.get("A");
        cache.get("B");
        
        // Swap to LFU
        cache.changePolicy(EvictionPolicy.LFU);
        
        cache.put("D", "4"); // Evicts C (implicit LRU tiebreaker, or lowest freq)
        
        assertNull(cache.get("C"));
        assertEquals("1", cache.get("A"));
        assertEquals("2", cache.get("B"));
        assertEquals("4", cache.get("D"));
        cache.shutdown();
    }
}
