package tests;
import org.junit.jupiter.api.*;
import v1_simple.*;
import v2_realistic.*;
import v3_production.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * JUnit 5 tests for cache implementations.
 */
public class CacheTest {

    private static final class TestDataSource<K, V> implements WriteThruCache.DataSource<K, V> {
        private final ConcurrentMap<K, V> values = new ConcurrentHashMap<>();
        private final AtomicInteger loads = new AtomicInteger();
        private volatile long delayMillis;

        void seed(K key, V value) {
            values.put(key, value);
        }

        void setDelay(long delayMillis) {
            this.delayMillis = delayMillis;
        }

        @Override
        public V get(K key) {
            loads.incrementAndGet();
            if (delayMillis > 0) {
                try {
                    Thread.sleep(delayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException(e);
                }
            }
            return values.get(key);
        }

        @Override
        public void put(K key, V value) {
            values.put(key, value);
        }

        @Override
        public void delete(K key) {
            values.remove(key);
        }
    }

    @Nested
    @DisplayName("SimpleCache Tests")
    class SimpleCacheTests {

        @Test
        @DisplayName("Should store and retrieve values")
        void testPutAndGet() {
            SimpleCache<String, String> cache = new SimpleCache<>(60);

            cache.put("key", "value");

            assertEquals("value", cache.get("key"));
            assertTrue(cache.containsKey("key"));
        }

        @Test
        @DisplayName("Should return null for missing keys")
        void testCacheMiss() {
            SimpleCache<String, String> cache = new SimpleCache<>(60);

            assertNull(cache.get("nonexistent"));
            assertFalse(cache.containsKey("nonexistent"));
        }

        @Test
        @DisplayName("Should expire entries after TTL")
        void testTTLExpiration() throws InterruptedException {
            SimpleCache<String, String> cache = new SimpleCache<>(60);

            cache.put("key", "value", 50);
            Thread.sleep(80);

            assertNull(cache.get("key"));
            assertFalse(cache.containsKey("key"));
        }

        @Test
        @DisplayName("Should remove entries")
        void testRemove() {
            SimpleCache<String, String> cache = new SimpleCache<>(60);

            cache.put("key", "value");
            cache.remove("key");

            assertNull(cache.get("key"));
            assertEquals(0, cache.size());
        }
    }

    @Nested
    @DisplayName("LRUCache Tests")
    class LRUCacheTests {

        @Test
        @DisplayName("Should evict least recently used when at capacity")
        void testLRUEviction() {
            LRUCache<String, String> cache = new LRUCache<>(2, 60);

            cache.put("A", "1");
            cache.put("B", "2");
            assertEquals("1", cache.get("A"));
            cache.put("C", "3");

            assertEquals("1", cache.get("A"));
            assertNull(cache.get("B"));
            assertEquals("3", cache.get("C"));
            assertEquals(1, cache.getEvictions());
        }

        @Test
        @DisplayName("Should track hit rate correctly")
        void testHitRateTracking() {
            LRUCache<String, String> cache = new LRUCache<>(10, 60);
            cache.put("key", "value");

            cache.get("key");
            cache.get("key");
            cache.get("missing");
            cache.get("missing2");

            assertEquals(2, cache.getHits());
            assertEquals(2, cache.getMisses());
            assertEquals(50.0, cache.getHitRate(), 0.01);
        }

        @Test
        @DisplayName("Should compute and cache on miss")
        void testGetOrCompute() {
            LRUCache<String, Integer> cache = new LRUCache<>(10, 60);
            AtomicInteger computeCount = new AtomicInteger(0);

            Integer result1 = cache.getOrCompute("key", () -> {
                computeCount.incrementAndGet();
                return 42;
            });
            Integer result2 = cache.getOrCompute("key", () -> {
                computeCount.incrementAndGet();
                return 42;
            });

            assertEquals(42, result1);
            assertEquals(42, result2);
            assertEquals(1, computeCount.get());
        }

        @Test
        @DisplayName("Should respect capacity limit")
        void testCapacityLimit() {
            LRUCache<Integer, String> cache = new LRUCache<>(3, 60);

            for (int i = 0; i < 10; i++) {
                cache.put(i, "value" + i);
            }

            assertEquals(3, cache.size());
            assertEquals(7, cache.getEvictions());
        }
    }

    @Nested
    @DisplayName("WriteThruCache Tests")
    class WriteThruCacheTests {

        @Test
        @DisplayName("Should write through to data source")
        void testWriteThrough() {
            TestDataSource<String, String> ds = new TestDataSource<>();
            WriteThruCache<String, String> cache = new WriteThruCache<>(10, 60, ds);
            try {
                cache.put("key", "value");

                assertEquals("value", ds.values.get("key"));
                assertEquals("value", cache.get("key"));
                assertEquals(1, cache.stats().writeThrus());
            } finally {
                cache.shutdown();
            }
        }

        @Test
        @DisplayName("Should load from data source on miss")
        void testLoadOnMiss() {
            TestDataSource<String, String> ds = new TestDataSource<>();
            ds.seed("key", "fromDB");
            WriteThruCache<String, String> cache = new WriteThruCache<>(10, 60, ds);
            try {
                assertEquals("fromDB", cache.get("key"));
                assertEquals("fromDB", cache.get("key"));

                assertEquals(1, ds.loads.get());
                assertEquals(1, cache.stats().loads());
                assertEquals(1, cache.stats().hits());
            } finally {
                cache.shutdown();
            }
        }

        @Test
        @DisplayName("Should prevent cache stampede")
        void testStampedePrevention() throws Exception {
            TestDataSource<String, String> ds = new TestDataSource<>();
            ds.seed("key", "value");
            ds.setDelay(50);
            WriteThruCache<String, String> cache = new WriteThruCache<>(10, 60, ds);
            ExecutorService executor = Executors.newFixedThreadPool(10);
            try {
                List<Callable<String>> tasks = new ArrayList<>();
                for (int i = 0; i < 10; i++) {
                    tasks.add(() -> cache.get("key"));
                }

                List<Future<String>> futures = executor.invokeAll(tasks);
                for (Future<String> future : futures) {
                    assertEquals("value", future.get());
                }

                assertEquals(1, ds.loads.get());
                assertEquals(1, cache.stats().loads());
            } finally {
                executor.shutdownNow();
                cache.shutdown();
            }
        }

        @Test
        @DisplayName("Should track statistics correctly")
        void testStatistics() {
            TestDataSource<String, String> ds = new TestDataSource<>();
            ds.seed("key", "value");
            WriteThruCache<String, String> cache = new WriteThruCache<>(10, 60, ds);
            try {
                cache.get("key");
                cache.get("key");
                cache.get("key");
                cache.put("new", "v");

                assertEquals(2, cache.stats().hits());
                assertEquals(1, cache.stats().misses());
                assertEquals(1, cache.stats().loads());
                assertEquals(1, cache.stats().writeThrus());
            } finally {
                cache.shutdown();
            }
        }

        @Test
        @DisplayName("Should handle concurrent access")
        void testConcurrentAccess() throws Exception {
            TestDataSource<Integer, String> ds = new TestDataSource<>();
            WriteThruCache<Integer, String> cache = new WriteThruCache<>(100, 60, ds);
            ExecutorService executor = Executors.newFixedThreadPool(10);
            try {
                List<Callable<Void>> tasks = new ArrayList<>();
                for (int i = 0; i < 1000; i++) {
                    final int key = i % 50;
                    tasks.add(() -> {
                        cache.put(key, "value" + key);
                        assertEquals("value" + key, cache.get(key));
                        return null;
                    });
                }

                for (Future<Void> future : executor.invokeAll(tasks)) {
                    future.get();
                }

                assertTrue(cache.size() <= 100);
                assertEquals(50, ds.values.size());
            } finally {
                executor.shutdownNow();
                cache.shutdown();
            }
        }
    }
}
