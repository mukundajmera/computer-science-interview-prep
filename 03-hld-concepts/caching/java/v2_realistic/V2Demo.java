package v2_realistic;
/**
 * Demo: LRU Cache Usage
 * 
 * Demonstrates:
 * - LRU eviction when capacity is exceeded
 * - Cache statistics and hit rates
 * - getOrCompute pattern for simplified usage
 */
public class V2Demo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== LRU Cache Demo ===\n");
        
        // Create cache with capacity of 3 entries, 60 second TTL
        LRUCache<String, String> cache = new LRUCache<>(3, 60);
        
        // Demo 1: LRU Eviction
        System.out.println("1. LRU Eviction (capacity=3):");
        cache.put("A", "Value A");
        cache.put("B", "Value B");
        cache.put("C", "Value C");
        System.out.println("   Added A, B, C - Size: " + cache.size());
        
        // Access A to make it "recently used"
        cache.get("A");
        System.out.println("   Accessed A (now most recently used)");
        
        // Add D - should evict B (least recently used)
        cache.put("D", "Value D");
        System.out.println("   Added D - Size: " + cache.size());
        System.out.println("   A = " + cache.get("A"));  // Still exists
        System.out.println("   B = " + cache.get("B"));  // Evicted!
        System.out.println("   C = " + cache.get("C"));  // Still exists
        System.out.println("   D = " + cache.get("D"));  // Just added
        System.out.println("   " + cache.getStats());
        
        // Demo 2: Hit Rate Tracking
        System.out.println("\n2. Hit Rate Tracking:");
        cache.clear();
        
        // Simulate workload
        String[] keys = {"user:1", "user:2", "user:3", "user:1", "user:1", "user:2"};
        for (String key : keys) {
            String value = cache.get(key);
            if (value == null) {
                // Cache miss - "fetch from database"
                value = "Data for " + key;
                cache.put(key, value);
                System.out.println("   " + key + " -> MISS -> cached");
            } else {
                System.out.println("   " + key + " -> HIT");
            }
        }
        System.out.println("   " + cache.getStats());
        
        // Demo 3: getOrCompute Pattern
        System.out.println("\n3. getOrCompute Pattern:");
        cache.clear();
        
        // First call - computes and caches
        String result = cache.getOrCompute("product:42", () -> {
            System.out.println("   Computing value for product:42...");
            return fetchExpensiveData();
        });
        System.out.println("   Result: " + result);
        
        // Second call - returns cached value
        result = cache.getOrCompute("product:42", () -> {
            System.out.println("   Computing value for product:42...");
            return fetchExpensiveData();
        });
        System.out.println("   Result: " + result);
        System.out.println("   " + cache.getStats());
        
        // Demo 4: TTL with LRU
        System.out.println("\n4. TTL with LRU:");
        LRUCache<String, String> shortTtlCache = new LRUCache<>(10, 1);  // 1 second TTL
        
        shortTtlCache.put("temp", "temporary data");
        System.out.println("   temp = " + shortTtlCache.get("temp"));
        
        Thread.sleep(1100);
        System.out.println("   After 1.1 seconds:");
        System.out.println("   temp = " + shortTtlCache.get("temp"));  // Expired
        
        // Demo 5: Simulating realistic workload
        System.out.println("\n5. Simulating Workload:");
        simulateWorkload();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static String fetchExpensiveData() {
        // Simulate expensive operation
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Expensive computed data";
    }
    
    private static void simulateWorkload() {
        LRUCache<Integer, String> cache = new LRUCache<>(100, 300);
        int totalRequests = 1000;
        
        // Simulate zipf-like distribution (some keys much more popular)
        java.util.Random random = new java.util.Random(42);
        
        for (int i = 0; i < totalRequests; i++) {
            // 80% of requests go to 20% of keys (Pareto principle)
            int key;
            if (random.nextDouble() < 0.8) {
                key = random.nextInt(20);  // Hot keys
            } else {
                key = random.nextInt(200);  // Cold keys
            }
            
            cache.getOrCompute(key, () -> "Data for key " + key);
        }
        
        System.out.println("   After " + totalRequests + " requests:");
        System.out.println("   " + cache.getStats());
        System.out.printf("   Expected high hit rate due to Pareto distribution%n");
    }
}
