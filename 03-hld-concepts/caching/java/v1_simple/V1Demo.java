package v1_simple;
/**
 * Demo: Simple Cache Usage
 * 
 * This demonstrates basic cache operations including:
 * - Storing and retrieving values
 * - TTL-based expiration
 * - Cache miss scenarios
 */
public class V1Demo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Simple Cache Demo ===\n");
        
        // Create cache with 5 second default TTL
        SimpleCache<String, String> cache = new SimpleCache<>(5);
        
        // Demo 1: Basic put and get
        System.out.println("1. Basic Operations:");
        cache.put("user:1", "Alice");
        cache.put("user:2", "Bob");
        
        System.out.println("   user:1 = " + cache.get("user:1"));  // Alice
        System.out.println("   user:2 = " + cache.get("user:2"));  // Bob
        System.out.println("   user:3 = " + cache.get("user:3"));  // null (cache miss)
        System.out.println("   Cache size: " + cache.size());
        
        // Demo 2: TTL expiration
        System.out.println("\n2. TTL Expiration:");
        cache.put("session:abc", "session_data", 2000);  // 2 second TTL
        System.out.println("   session:abc = " + cache.get("session:abc"));  // session_data
        
        System.out.println("   Waiting 2.5 seconds...");
        Thread.sleep(2500);
        
        System.out.println("   session:abc = " + cache.get("session:abc"));  // null (expired)
        
        // Demo 3: Simulating cache-aside pattern
        System.out.println("\n3. Cache-Aside Pattern:");
        String productId = "product:42";
        String product = getProductWithCache(cache, productId);
        System.out.println("   First call (cache miss): " + product);
        
        product = getProductWithCache(cache, productId);
        System.out.println("   Second call (cache hit): " + product);
        
        // Demo 4: Cache invalidation
        System.out.println("\n4. Cache Invalidation:");
        cache.put("config:version", "v1.0");
        System.out.println("   Before invalidation: " + cache.get("config:version"));
        
        cache.remove("config:version");
        System.out.println("   After invalidation: " + cache.get("config:version"));
        
        // Demo 5: Cleanup expired entries
        System.out.println("\n5. Cleanup:");
        cache.put("temp:1", "data1", 100);  // Very short TTL
        cache.put("temp:2", "data2", 100);
        Thread.sleep(150);
        
        System.out.println("   Size before cleanup: " + cache.size());
        cache.cleanup();
        System.out.println("   Size after cleanup: " + cache.size());
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    /**
     * Demonstrates cache-aside pattern:
     * 1. Check cache first
     * 2. On miss, fetch from "database" (simulated)
     * 3. Store in cache
     * 4. Return value
     */
    private static String getProductWithCache(SimpleCache<String, String> cache, String productId) {
        // Try cache first
        String product = cache.get(productId);
        if (product != null) {
            System.out.println("   [CACHE HIT]");
            return product;
        }
        
        // Cache miss - fetch from "database"
        System.out.println("   [CACHE MISS] - Fetching from database...");
        product = fetchFromDatabase(productId);
        
        // Store in cache for future requests
        cache.put(productId, product);
        
        return product;
    }
    
    /**
     * Simulates a slow database call.
     */
    private static String fetchFromDatabase(String productId) {
        // Simulate database latency
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Product data for " + productId;
    }
}
