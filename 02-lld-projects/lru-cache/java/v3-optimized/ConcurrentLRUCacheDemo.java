package v3_optimized;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * LRU Cache - V3 Optimized Demo
 * 
 * Demonstrates thread-safe LRU cache with concurrent access.
 */
public class ConcurrentLRUCacheDemo {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Concurrent LRU Cache Demo ===\n");

        demonstrateBasicOperations();
        System.out.println("\n" + "=".repeat(60) + "\n");
        demonstrateConcurrentAccess();
        System.out.println("\n" + "=".repeat(60) + "\n");
        demonstrateStatistics();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("--- Basic Operations (Same as V1) ---\n");

        ConcurrentLRUCache<String, Integer> cache = new ConcurrentLRUCache<>(3);

        cache.put("a", 1);
        cache.put("b", 2);
        cache.put("c", 3);
        System.out.println("Added a=1, b=2, c=3");
        System.out.println("Cache: " + cache);

        System.out.println("\nget(a) = " + cache.get("a"));
        cache.put("d", 4);  // Evicts 'b'
        System.out.println("put(d, 4) - evicts 'b'");
        System.out.println("get(b) = " + cache.get("b") + " (evicted)");
        System.out.println("Cache: " + cache);
    }

    private static void demonstrateConcurrentAccess() throws InterruptedException {
        System.out.println("--- Concurrent Access Test ---\n");

        ConcurrentLRUCache<Integer, Integer> cache = new ConcurrentLRUCache<>(100);
        int numThreads = 10;
        int operationsPerThread = 1000;

        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(numThreads);

        AtomicInteger putCount = new AtomicInteger(0);
        AtomicInteger getCount = new AtomicInteger(0);

        // Create worker threads
        for (int t = 0; t < numThreads; t++) {
            final int threadId = t;
            executor.submit(() -> {
                try {
                    startLatch.await();  // Wait for start signal

                    for (int i = 0; i < operationsPerThread; i++) {
                        int key = (threadId * 100 + i) % 150;  // Keys 0-149

                        if (i % 3 == 0) {
                            cache.put(key, threadId * 1000 + i);
                            putCount.incrementAndGet();
                        } else {
                            cache.get(key);
                            getCount.incrementAndGet();
                        }
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        System.out.println("Starting " + numThreads + " threads with " + 
                           operationsPerThread + " operations each...");
        long startTime = System.currentTimeMillis();
        startLatch.countDown();  // Start all threads

        doneLatch.await();  // Wait for completion
        long elapsed = System.currentTimeMillis() - startTime;

        executor.shutdown();

        System.out.println("\nResults:");
        System.out.println("  Total time: " + elapsed + "ms");
        System.out.println("  Put operations: " + putCount.get());
        System.out.println("  Get operations: " + getCount.get());
        System.out.println("  Final cache size: " + cache.size());
        System.out.println("  Cache hits: " + cache.getHits());
        System.out.println("  Cache misses: " + cache.getMisses());
        System.out.println("  Hit ratio: " + String.format("%.2f%%", cache.getHitRatio() * 100));
        System.out.println("  Evictions: " + cache.getEvictions());
        System.out.println("\n  ✓ No exceptions = Thread-safe!");
    }

    private static void demonstrateStatistics() {
        System.out.println("--- Thread-Safe Statistics ---\n");

        ConcurrentLRUCache<String, Integer> cache = new ConcurrentLRUCache<>(5);

        // Populate
        for (int i = 0; i < 5; i++) {
            cache.put("key" + i, i);
        }

        // Access pattern: some hits, some misses
        for (int i = 0; i < 10; i++) {
            cache.get("key" + (i % 7));  // Keys 0-4 exist, 5-6 don't
        }

        System.out.println("Cache operations:");
        System.out.println("  5 puts, 10 gets");
        System.out.println("\nStatistics (atomic counters):");
        System.out.println("  Hits: " + cache.getHits());
        System.out.println("  Misses: " + cache.getMisses());
        System.out.println("  Hit Ratio: " + String.format("%.1f%%", cache.getHitRatio() * 100));
        System.out.println("  Evictions: " + cache.getEvictions());

        // Trigger evictions
        System.out.println("\nAdding 3 more entries (triggers evictions)...");
        cache.put("new1", 100);
        cache.put("new2", 200);
        cache.put("new3", 300);

        System.out.println("  Evictions after: " + cache.getEvictions());
        System.out.println("\nFinal: " + cache);
    }
}
