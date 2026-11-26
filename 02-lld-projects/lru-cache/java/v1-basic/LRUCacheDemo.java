package v1_basic;

/**
 * LRU Cache - V1 Basic Demo
 * 
 * Demonstrates the LRU cache in action.
 */
public class LRUCacheDemo {

    public static void main(String[] args) {
        System.out.println("=== LRU Cache Demo ===\n");

        // Create cache with capacity 3
        LRUCache<String, Integer> cache = new LRUCache<>(3);
        System.out.println("Created cache with capacity 3\n");

        // Test 1: Basic operations
        System.out.println("Test 1: Basic put and get operations");
        cache.put("a", 1);
        System.out.println("put(a, 1): " + cache);

        cache.put("b", 2);
        System.out.println("put(b, 2): " + cache);

        cache.put("c", 3);
        System.out.println("put(c, 3): " + cache);

        System.out.println("get(a) = " + cache.get("a"));
        System.out.println("After get(a): " + cache);

        // Test 2: Eviction
        System.out.println("\nTest 2: Eviction on capacity overflow");
        cache.put("d", 4);
        System.out.println("put(d, 4): " + cache);
        System.out.println("get(b) = " + cache.get("b") + " (should be null - evicted)");

        // Test 3: Update existing key
        System.out.println("\nTest 3: Update existing key");
        cache.put("a", 100);
        System.out.println("put(a, 100): " + cache);
        System.out.println("get(a) = " + cache.get("a") + " (should be 100)");

        // Test 4: Remove
        System.out.println("\nTest 4: Remove operation");
        Integer removed = cache.remove("c");
        System.out.println("remove(c) = " + removed);
        System.out.println("After remove: " + cache);

        // Test 5: Size and capacity
        System.out.println("\nTest 5: Size and capacity");
        System.out.println("size() = " + cache.size());
        System.out.println("getCapacity() = " + cache.getCapacity());
        System.out.println("containsKey(a) = " + cache.containsKey("a"));
        System.out.println("containsKey(c) = " + cache.containsKey("c"));

        // Test 6: Clear
        System.out.println("\nTest 6: Clear cache");
        cache.clear();
        System.out.println("After clear(): " + cache);

        // Test 7: Edge case - single capacity
        System.out.println("\nTest 7: Single capacity cache");
        LRUCache<String, String> singleCache = new LRUCache<>(1);
        singleCache.put("only", "one");
        System.out.println("After put(only, one): " + singleCache);
        singleCache.put("new", "entry");
        System.out.println("After put(new, entry): " + singleCache);
        System.out.println("get(only) = " + singleCache.get("only") + " (evicted)");
        System.out.println("get(new) = " + singleCache.get("new"));

        System.out.println("\n=== Demo Complete ===");
    }
}
