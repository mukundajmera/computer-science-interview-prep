package v3_production;
import java.util.Map;
import java.util.concurrent.*;

/**
 * Demo: Production Write-Through Cache
 * 
 * Demonstrates production-level caching patterns:
 * - Write-through to backing store
 * - Cache stampede prevention
 * - Concurrent access handling
 * - Statistics monitoring
 */
public class V3Demo {
    
    public static void main(String[] args) throws Exception {
        System.out.println("=== Production Write-Through Cache Demo ===\n");
        
        // Create an in-memory "database" as backing store
        InMemoryDataSource dataSource = new InMemoryDataSource();
        
        // Pre-populate database
        dataSource.put("user:1", "{\"name\": \"Alice\", \"email\": \"alice@example.com\"}");
        dataSource.put("user:2", "{\"name\": \"Bob\", \"email\": \"bob@example.com\"}");
        dataSource.put("product:1", "{\"name\": \"Widget\", \"price\": 9.99}");
        
        // Create cache with capacity=100, TTL=60s
        WriteThruCache<String, String> cache = new WriteThruCache<>(100, 60, dataSource);
        
        try {
            // Demo 1: Cache-aside reads
            System.out.println("1. Cache-Aside Read Pattern:");
            System.out.println("   Getting user:1 (cache miss - loads from DB):");
            String user1 = cache.get("user:1");
            System.out.println("   Result: " + user1);
            System.out.println("   Stats: " + cache.stats());
            
            System.out.println("\n   Getting user:1 again (cache hit):");
            user1 = cache.get("user:1");
            System.out.println("   Result: " + user1);
            System.out.println("   Stats: " + cache.stats());
            
            // Demo 2: Write-through
            System.out.println("\n2. Write-Through Pattern:");
            String newUser = "{\"name\": \"Charlie\", \"email\": \"charlie@example.com\"}";
            cache.put("user:3", newUser);
            System.out.println("   Written user:3 to cache and database");
            System.out.println("   Cache value: " + cache.get("user:3"));
            System.out.println("   DB value: " + dataSource.get("user:3"));
            System.out.println("   Stats: " + cache.stats());
            
            // Demo 3: Cache stampede prevention
            System.out.println("\n3. Cache Stampede Prevention:");
            System.out.println("   Simulating 10 concurrent requests for same key...");
            
            cache.invalidate("user:1");  // Clear cache
            dataSource.setDelay(100);     // Add 100ms DB latency
            
            ExecutorService executor = Executors.newFixedThreadPool(10);
            CountDownLatch latch = new CountDownLatch(10);
            
            long start = System.currentTimeMillis();
            for (int i = 0; i < 10; i++) {
                executor.submit(() -> {
                    try {
                        cache.get("user:1");
                    } finally {
                        latch.countDown();
                    }
                });
            }
            latch.await();
            long elapsed = System.currentTimeMillis() - start;
            
            System.out.println("   Completed in " + elapsed + "ms");
            System.out.println("   DB calls: " + dataSource.getCallCount());
            System.out.println("   (Without stampede prevention, would be 10 DB calls)");
            System.out.println("   Stats: " + cache.stats());
            
            dataSource.setDelay(0);
            dataSource.resetCallCount();
            executor.shutdown();
            
            // Demo 4: Concurrent writes
            System.out.println("\n4. Concurrent Write Operations:");
            ExecutorService writers = Executors.newFixedThreadPool(5);
            CountDownLatch writeLatch = new CountDownLatch(100);
            
            for (int i = 0; i < 100; i++) {
                final int idx = i;
                writers.submit(() -> {
                    try {
                        cache.put("key:" + (idx % 20), "value:" + idx);
                    } finally {
                        writeLatch.countDown();
                    }
                });
            }
            writeLatch.await();
            writers.shutdown();
            
            System.out.println("   Completed 100 concurrent writes");
            System.out.println("   Cache size: " + cache.size());
            System.out.println("   Stats: " + cache.stats());
            
            // Demo 5: Cache statistics
            System.out.println("\n5. Monitoring & Statistics:");
            System.out.println("   " + cache.stats());
            System.out.printf("   Hit Rate: %.2f%%%n", cache.stats().hitRate());
            System.out.println("   Total Loads from DB: " + cache.stats().loads());
            System.out.println("   Write-throughs: " + cache.stats().writeThrus());
            
            // Demo 6: Cache invalidation
            System.out.println("\n6. Cache Invalidation:");
            System.out.println("   Before invalidation - user:1 in cache: " + (cache.get("user:1") != null));
            cache.invalidate("user:1");
            
            // Need to check without triggering a load
            System.out.println("   After invalidation - triggers reload on next access");
            long loadsBefore = cache.stats().loads();
            cache.get("user:1");
            System.out.println("   New load triggered: " + (cache.stats().loads() > loadsBefore));
            
        } finally {
            cache.shutdown();
        }
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    /**
     * Simulated database with configurable latency.
     */
    static class InMemoryDataSource implements WriteThruCache.DataSource<String, String> {
        private final ConcurrentHashMap<String, String> store = new ConcurrentHashMap<>();
        private volatile int delayMs = 0;
        private final java.util.concurrent.atomic.AtomicInteger callCount = 
            new java.util.concurrent.atomic.AtomicInteger();
        
        @Override
        public String get(String key) {
            callCount.incrementAndGet();
            if (delayMs > 0) {
                try {
                    Thread.sleep(delayMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            return store.get(key);
        }
        
        @Override
        public void put(String key, String value) {
            store.put(key, value);
        }
        
        @Override
        public void delete(String key) {
            store.remove(key);
        }
        
        void setDelay(int ms) {
            this.delayMs = ms;
        }
        
        int getCallCount() {
            return callCount.get();
        }
        
        void resetCallCount() {
            callCount.set(0);
        }
    }
}
