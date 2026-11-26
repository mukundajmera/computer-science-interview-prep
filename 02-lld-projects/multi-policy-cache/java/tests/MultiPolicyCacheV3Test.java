package v3_optimized;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;

public class MultiPolicyCacheV3Test {

    @Test
    public void testV3TtlActiveBackgroundExpiry() throws InterruptedException {
        MultiPolicyCache<String, String> cache = new MultiPolicyCache<>(100, EvictionPolicy.LRU, 4);
        
        for (int i = 0; i < 20; i++) {
            cache.put("key" + i, "val", 100);
        }
        
        Thread.sleep(1500); // Wait for background sweeper
        
        // Some items should be swept
        assertTrue(cache.size() < 20);
        cache.shutdown();
    }

    @Test
    public void testV3ReadConcurrencyHighThroughput() throws InterruptedException {
        MultiPolicyCache<String, Integer> cache = new MultiPolicyCache<>(4096, EvictionPolicy.LFU, 16);
        
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            final int workerId = i;
            Thread t = new Thread(() -> {
                for (int j = 0; j < 100; j++) {
                    String key = "key_" + workerId + "_" + j;
                    cache.put(key, j);
                    cache.get(key);
                }
            });
            threads.add(t);
            t.start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        assertTrue(cache.size() >= 800);
        cache.shutdown();
    }

    @Test
    public void testV3ThreadSafeStatistics() throws InterruptedException {
        MultiPolicyCache<String, Integer> cache = new MultiPolicyCache<>(100, EvictionPolicy.FIFO, 4);
        
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            Thread t = new Thread(() -> {
                for (int j = 0; j < 50; j++) {
                    cache.put("key_" + j, j);
                    cache.get("key_" + j);
                    cache.get("miss_" + j);
                }
            });
            threads.add(t);
            t.start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        MultiPolicyCache.CacheStats stats = cache.getStats();
        assertEquals(200, stats.hits);
        assertEquals(200, stats.misses);
        assertTrue(stats.evictions >= 0);
        cache.shutdown();
    }

    @Test
    public void testV3SegmentedEviction() {
        MultiPolicyCache<String, Integer> cache = new MultiPolicyCache<>(16, EvictionPolicy.LRU, 4);
        
        for (int i = 0; i < 100; i++) {
            cache.put("key_" + i, i);
        }
        
        assertTrue(cache.size() <= 16);
        assertTrue(cache.getStats().evictions > 0);
        cache.shutdown();
    }
}
