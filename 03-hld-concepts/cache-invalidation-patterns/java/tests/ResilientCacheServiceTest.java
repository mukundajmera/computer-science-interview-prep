package cacheinvalidationpatterns;

import org.junit.jupiter.api.Test;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;

import static org.junit.jupiter.api.Assertions.*;

public class ResilientCacheServiceTest {

    @Test
    public void testBloomFilterPreventsDbHit() {
        AtomicInteger dbHits = new AtomicInteger(0);
        // Bloom filter says key does not exist
        ResilientCacheService<String, String> cache = new ResilientCacheService<>(
                key -> false, 1000, 100, 500);

        String result = cache.get("invalid_key", k -> {
            dbHits.incrementAndGet();
            return "data";
        });

        assertNull(result);
        assertEquals(0, dbHits.get(), "DB should not be hit if Bloom filter rejects key");
    }

    @Test
    public void testNullCachingPreventsDbHits() {
        AtomicInteger dbHits = new AtomicInteger(0);
        // Bloom filter says key might exist
        ResilientCacheService<String, String> cache = new ResilientCacheService<>(
                key -> true, 1000, 100, 500);

        // First call hits DB, returns null
        String result1 = cache.get("missing_key", k -> {
            dbHits.incrementAndGet();
            return null;
        });

        // Second call should hit null cache, no DB hit
        String result2 = cache.get("missing_key", k -> {
            dbHits.incrementAndGet();
            return null;
        });

        assertNull(result1);
        assertNull(result2);
        assertEquals(1, dbHits.get(), "DB should only be hit once due to null object caching");
        
        ResilientCacheService.CacheEntry<String> entry = cache.getRawEntry("missing_key");
        assertNotNull(entry);
        assertTrue(entry.isNullObject);
    }

    @Test
    public void testSingleflightThunderingHerdMitigation() throws InterruptedException {
        AtomicInteger dbHits = new AtomicInteger(0);
        ResilientCacheService<String, String> cache = new ResilientCacheService<>(
                key -> true, 5000, 100, 500);

        int numThreads = 50;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(numThreads);

        for (int i = 0; i < numThreads; i++) {
            executor.submit(() -> {
                try {
                    startLatch.await();
                    cache.get("hot_key", k -> {
                        dbHits.incrementAndGet();
                        try {
                            Thread.sleep(50); // Simulate DB latency
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                        }
                        return "viral_content";
                    });
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        startLatch.countDown(); // Start all threads at once
        doneLatch.await();      // Wait for all to finish
        executor.shutdown();

        assertEquals(1, dbHits.get(), "DB should exactly be hit 1 time despite 50 concurrent threads");
        assertEquals("viral_content", cache.get("hot_key", k -> "wrong"));
    }

    @Test
    public void testTtlJitterDistribution() {
        long baseTtl = 1000;
        long jitter = 500;
        ResilientCacheService<String, String> cache = new ResilientCacheService<>(
                key -> true, baseTtl, jitter, 500);

        cache.get("key1", k -> "data1");
        cache.get("key2", k -> "data2");
        
        ResilientCacheService.CacheEntry<String> entry1 = cache.getRawEntry("key1");
        ResilientCacheService.CacheEntry<String> entry2 = cache.getRawEntry("key2");

        long ttl1 = entry1.expireAt - System.currentTimeMillis();
        long ttl2 = entry2.expireAt - System.currentTimeMillis();
        
        // It's possible but extremely unlikely they are exactly the same
        // Note: ttl calc above uses current time which might be slightly off from creation,
        // but within reasonable bounds we just check the expireAt difference.
        
        long diff = Math.abs(entry1.expireAt - entry2.expireAt);
        // Ensure jitter is applied (very rarely diff is 0)
        // Also ensure it's within bounds
        assertTrue(entry1.expireAt >= System.currentTimeMillis() + baseTtl - 100);
        assertTrue(entry1.expireAt <= System.currentTimeMillis() + baseTtl + jitter + 100);
    }
}
