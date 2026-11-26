package v3_production;

import java.util.*;

/**
 * Demo for production-grade consistent hash sharding.
 */
public class V3Demo {
    public static void main(String[] args) {
        System.out.println("=== Consistent Hash Sharding Demo ===\n");

        System.out.println("1. Remap Comparison: Modulo vs Consistent Hash Sharding");
        remapComparisonDemo();

        System.out.println("\n2. Replication and Failure Behavior");
        replicationAndFailureDemo();

        System.out.println("\n3. Hotspot Narrative and Mitigation");
        hotspotDemo();

        System.out.println("\n4. Rebalance Summary");
        rebalanceSummaryDemo();

        System.out.println("\n=== Demo Complete ===");
    }

    private static void remapComparisonDemo() {
        int totalKeys = 10000;
        List<String> keys = new ArrayList<>(totalKeys);
        for (int i = 0; i < totalKeys; i++) {
            keys.add("user_" + i);
        }

        int moduloMoved = 0;
        for (String key : keys) {
            int before = Math.floorMod(key.hashCode(), 3);
            int after = Math.floorMod(key.hashCode(), 4);
            if (before != after) {
                moduloMoved++;
            }
        }

        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 1);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");

        Map<String, String> beforeMap = new HashMap<>();
        for (String key : keys) {
            beforeMap.put(key, router.getShardForKey(key));
        }

        router.addShard("shard_4");

        int consistentMoved = 0;
        for (String key : keys) {
            String after = router.getShardForKey(key);
            if (!Objects.equals(beforeMap.get(key), after)) {
                consistentMoved++;
            }
        }

        System.out.printf("   Modulo (3 -> 4 shards): moved %d/%d (%.1f%%)%n",
                moduloMoved, totalKeys, moduloMoved * 100.0 / totalKeys);
        System.out.printf("   Consistent hash (3 -> 4 shards): moved %d/%d (%.1f%%)%n",
                consistentMoved, totalKeys, consistentMoved * 100.0 / totalKeys);
    }

    private static void replicationAndFailureDemo() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 2);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");

        String key = "critical:order:123";
        Map<String, Object> value = new HashMap<>();
        value.put("order_id", 123);
        value.put("status", "confirmed");
        router.put(key, value);

        System.out.printf("   Replicas for %s: %s%n", key, router.getShardsForReplication(key));

        String primary = router.getShardForKey(key);
        router.markShardUnhealthy(primary);
        System.out.printf("   Marked primary unhealthy: %s%n", primary);

        Map<String, Object> read = router.get(key);
        System.out.printf("   Read from healthy replica path: %s%n", read);
    }

    private static void hotspotDemo() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 2);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");

        String hotKey = "user:celebrity";
        Map<String, Integer> ownerCount = new HashMap<>();

        for (int i = 0; i < 5000; i++) {
            String owner = router.getShardForKey(hotKey);
            ownerCount.merge(owner, 1, Integer::sum);
        }

        System.out.printf("   Hot key ownership counts: %s%n", ownerCount);
        System.out.println("   Note: consistent hash improves remap behavior, not hot-key popularity.");
        System.out.println("   Mitigations: replica reads, key bucketing, cache and rate limits.");
    }

    private static void rebalanceSummaryDemo() {
        ConsistentHashShardRouter router = new ConsistentHashShardRouter(100, 1);
        router.addShard("shard_1");
        router.addShard("shard_2");
        router.addShard("shard_3");

        for (int i = 0; i < 3000; i++) {
            Map<String, Object> row = new HashMap<>();
            row.put("id", i);
            router.put("user_" + i, row);
        }

        System.out.println("   Distribution before rebalance:");
        router.printDistribution();

        router.addShard("shard_4");
        System.out.println("   Distribution after adding shard_4 (new writes):");
        for (int i = 3000; i < 5000; i++) {
            Map<String, Object> row = new HashMap<>();
            row.put("id", i);
            router.put("user_" + i, row);
        }
        router.printDistribution();

        System.out.printf("   Cluster summary: shards=%d virtual_nodes=%d%n",
                router.getShardCount(), router.getVirtualNodeCount());
    }
}
