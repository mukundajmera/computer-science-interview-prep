package tests;

import v1_simple.HashShardRouter;
import v2_realistic.RangeShardRouter;
import v3_production.ConsistentHashShardRouter;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ShardingTest {

    public static void assertTrue(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    public static void assertEquals(int expected, int actual) {
        if (expected != actual) throw new AssertionError("Expected " + expected + " but got " + actual);
    }
    public static void assertEquals(long expected, long actual) {
        if (expected != actual) throw new AssertionError("Expected " + expected + " but got " + actual);
    }
    public static void assertEquals(Object expected, Object actual) {
        if (expected == null && actual == null) return;
        if (expected == null || !expected.equals(actual)) throw new AssertionError("Expected " + expected + " but got " + actual);
    }
    public static void assertNotNull(Object obj) {
        if (obj == null) throw new AssertionError("Expected not null");
    }
    public static void assertFalse(boolean condition) {
        if (condition) throw new AssertionError("Expected false");
    }
    public static void assertThrows(Class<? extends Throwable> expectedType, Runnable executable) {
        try {
            executable.run();
        } catch (Throwable actualException) {
            if (expectedType.isInstance(actualException)) {
                return;
            }
            throw new AssertionError("Expected " + expectedType.getName() + " but got " + actualException.getClass().getName());
        }
        throw new AssertionError("Expected " + expectedType.getName() + " to be thrown, but nothing was thrown.");
    }

    public static void main(String[] args) {
        testHashShardingDistribution();
        testHashShardingConsistency();
        testHashShardingGetAndPut();
        testRangeShardingRouting();
        testRangeShardingRangeQuery();
        testRangeShardingHealthCheck();
        testConsistentHashMinimalRedistribution();
        testConsistentHashReplication();
        testConsistentHashFailover();
        testConsistentHashRemoveShard();
        System.out.println("All tests passed!");
    }

    // V1 Tests - Hash Sharding
    static void testHashShardingDistribution() {
        HashShardRouter router = new HashShardRouter(4);
        
        // Insert 1000 items
        for (int i = 0; i < 1000; i++) {
            String key = "user_" + i;
            router.put(key, key, "data_" + i);
        }
        
        // Check distribution - each shard should have at least some items
        for (int i = 0; i < 4; i++) {
            assertTrue(router.getShardSize(i) > 0, 
                    "Shard " + i + " should have items");
        }
        
        assertEquals(1000, router.getTotalSize());
    }

    static void testHashShardingConsistency() {
        HashShardRouter router = new HashShardRouter(4);
        
        // Same key should always go to same shard
        String key = "test_user_123";
        int shard1 = router.getShardId(key);
        int shard2 = router.getShardId(key);
        int shard3 = router.getShardId(key);
        
        assertEquals(shard1, shard2);
        assertEquals(shard2, shard3);
    }

    static void testHashShardingGetAndPut() {
        HashShardRouter router = new HashShardRouter(4);
        
        router.put("user_1", "profile", "{\"name\": \"Alice\"}");
        router.put("user_1", "settings", "{\"theme\": \"dark\"}");
        
        assertEquals("{\"name\": \"Alice\"}", router.get("user_1", "profile"));
        assertEquals("{\"theme\": \"dark\"}", router.get("user_1", "settings"));
    }

    // V2 Tests - Range Sharding
    static void testRangeShardingRouting() {
        RangeShardRouter router = new RangeShardRouter();
        router.addShard("shard_1", 0, 1000);
        router.addShard("shard_2", 1000, 2000);
        router.addShard("shard_3", 2000, 3000);
        
        assertEquals("shard_1", router.routeToShard(500).shardId);
        assertEquals("shard_2", router.routeToShard(1500).shardId);
        assertEquals("shard_3", router.routeToShard(2500).shardId);
    }

    static void testRangeShardingRangeQuery() {
        RangeShardRouter router = new RangeShardRouter();
        router.addShard("shard_1", 0, 1000);
        router.addShard("shard_2", 1000, 2000);
        
        // Insert data
        for (int i = 0; i < 1500; i++) {
            Map<String, Object> data = new HashMap<>();
            data.put("id", i);
            router.put(i, data);
        }
        
        // Range query across shards
        List<Map<String, Object>> results = router.rangeQuery(500, 1200);
        
        // Should include items from 500-1199 (700 items)
        assertEquals(700, results.size());
    }

    static void testRangeShardingHealthCheck() {
        RangeShardRouter router = new RangeShardRouter();
        router.addShard("shard_1", 0, 1000);
        
        // Should work when healthy
        Map<String, Object> data = new HashMap<>();
        data.put("id", 500);
        router.put(500, data);
        
        // Mark unhealthy
        router.markShardUnhealthy("shard_1");
        
        // Should fail when unhealthy
        assertThrows(RuntimeException.class, () -> {
            router.put(600, data);
        });
    }

    // V3 Tests - Consistent Hash Sharding
    static void testConsistentHashMinimalRedistribution() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 1);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");
        
        // Track initial mapping
        Map<String, String> beforeMapping = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String key = "key_" + i;
            beforeMapping.put(key, router.getShardForKey(key));
        }
        
        // Add new shard
        router.addShard("shard_4");
        
        // Count changes
        int changed = 0;
        for (int i = 0; i < 1000; i++) {
            String key = "key_" + i;
            if (!beforeMapping.get(key).equals(router.getShardForKey(key))) {
                changed++;
            }
        }
        
        // With consistent hashing, roughly 1/4 (25%) should change
        // Allow range of 15-40% for randomness
        double changePercent = changed * 100.0 / 1000;
        assertTrue(changePercent < 40, 
                "Too many keys changed: " + changePercent + "%");
    }

    static void testConsistentHashReplication() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 3);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");
        
        List<String> replicas = router.getShardsForReplication("test_key");
        
        // Should get 3 unique replicas
        assertEquals(3, replicas.size());
        assertEquals(3L, replicas.stream().distinct().count());
    }

    static void testConsistentHashFailover() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 2);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");
        
        // Insert data
        Map<String, Object> data = new HashMap<>();
        data.put("value", "test");
        router.put("test_key", data);
        
        // Mark primary shard as unhealthy
        String primary = router.getShardForKey("test_key");
        router.markShardUnhealthy(primary);
        
        // Should still be able to read from replica
        Map<String, Object> retrieved = router.get("test_key");
        assertNotNull(retrieved);
        assertEquals("test", retrieved.get("value"));
    }

    static void testConsistentHashRemoveShard() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 1);
        router.addShard("shard_1");
        router.addShard("shard_2");
        
        // Insert data
        for (int i = 0; i < 100; i++) {
            Map<String, Object> data = new HashMap<>();
            data.put("id", i);
            router.put("key_" + i, data);
        }
        
        int initialTotal = router.getShardCount();
        
        // Remove shard
        Map<String, Map<String, Object>> migrated = router.removeShard("shard_1");
        
        // Should have data to migrate
        assertFalse(migrated.isEmpty());
        assertEquals(initialTotal - 1, router.getShardCount());
    }
}
