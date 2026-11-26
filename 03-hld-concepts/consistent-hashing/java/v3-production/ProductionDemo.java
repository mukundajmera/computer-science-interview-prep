import java.util.*;

/**
 * Demo: Production Consistent Hashing
 */
public class ProductionDemo {

    public static void main(String[] args) {
        System.out.println("=== Production Consistent Hash Demo ===\n");

        System.out.println("1. Remap Comparison: Modulo vs Consistent Hashing");
        remapComparisonDemo();

        System.out.println("\n2. Replication and Failure Handling");
        replicationAndFailureDemo();

        System.out.println("\n3. Hotspot Narrative and Mitigation");
        hotspotDemo();

        System.out.println("\n4. Bounded Load and Distribution");
        boundedLoadDemo();

        System.out.println("\n=== Demo Complete ===");
    }

    private static void remapComparisonDemo() {
        int totalKeys = 10000;
        List<String> keys = new ArrayList<>(totalKeys);
        for (int i = 0; i < totalKeys; i++) {
            keys.add("key-" + i);
        }

        int moduloMoved = 0;
        for (String key : keys) {
            int before = Math.floorMod(key.hashCode(), 3);
            int after = Math.floorMod(key.hashCode(), 4);
            if (before != after) {
                moduloMoved++;
            }
        }
        double moduloPct = moduloMoved * 100.0 / totalKeys;

        ProductionConsistentHash ring = new ProductionConsistentHash(100, 1, 1.0);
        ring.addNode("node-a");
        ring.addNode("node-b");
        ring.addNode("node-c");

        Map<String, String> beforeMap = new HashMap<>();
        for (String key : keys) {
            beforeMap.put(key, ring.lookup(key).getPrimaryNode());
        }

        ring.addNode("node-d");

        int consistentMoved = 0;
        for (String key : keys) {
            String after = ring.lookup(key).getPrimaryNode();
            if (!Objects.equals(beforeMap.get(key), after)) {
                consistentMoved++;
            }
        }
        double consistentPct = consistentMoved * 100.0 / totalKeys;

        System.out.printf("   Modulo (3 -> 4 nodes): moved %d/%d (%.1f%%)%n", moduloMoved, totalKeys, moduloPct);
        System.out.printf("   Consistent hash (3 -> 4 nodes): moved %d/%d (%.1f%%)%n", consistentMoved, totalKeys, consistentPct);
        System.out.println("   Expected: consistent hashing moves a bounded fraction of keys.");
    }

    private static void replicationAndFailureDemo() {
        ProductionConsistentHash ch = new ProductionConsistentHash(100, 3, 1.0);

        ch.addNode("node-a");
        ch.addNode("node-b");
        ch.addNode("node-c");
        ch.addNode("node-d");

        String key = "critical:data";
        ProductionConsistentHash.LookupResult healthy = ch.lookup(key);
        System.out.printf("   Healthy replicas for '%s': %s%n", key, healthy.getAllNodes());

        ch.setNodeHealth("node-a", false);
        ProductionConsistentHash.LookupResult degraded = ch.lookup(key);
        System.out.printf("   After node-a failure: %s%n", degraded.getAllNodes());

        ch.setNodeHealth("node-a", true);
        ProductionConsistentHash.LookupResult recovered = ch.lookup(key);
        System.out.printf("   After recovery: %s%n", recovered.getAllNodes());
    }

    private static void hotspotDemo() {
        ProductionConsistentHash ch = new ProductionConsistentHash(100, 2, 1.0);
        ch.addNode("node-a");
        ch.addNode("node-b");
        ch.addNode("node-c");

        String hotKey = "event:mega-concert";
        Map<String, Integer> ownership = new HashMap<>();
        for (int i = 0; i < 5000; i++) {
            String owner = ch.lookup(hotKey).getPrimaryNode();
            ownership.merge(owner, 1, Integer::sum);
        }

        System.out.printf("   Hot key '%s' primary ownership: %s%n", hotKey, ownership);
        System.out.println("   Note: ring placement alone does not remove hot-key traffic skew.");
        System.out.println("   Typical mitigations: replica reads, key bucketing, local cache, rate limits.");
    }

    private static void boundedLoadDemo() {
        ProductionConsistentHash ch = new ProductionConsistentHash(100, 1, 1.25);

        ch.addNode("node-a");
        ch.addNode("node-b");
        ch.addNode("node-c");

        for (int i = 0; i < 10000; i++) {
            ch.lookup("key-" + i);
        }

        Map<String, Long> dist = ch.getDistribution();
        System.out.println("   Per-node request distribution:");
        dist.forEach((node, count) -> System.out.printf("      %s: %d%n", node, count));

        double avg = dist.values().stream().mapToLong(Long::longValue).average().orElse(0.0);
        double maxDev = dist.values().stream()
            .mapToDouble(v -> Math.abs(v - avg) / Math.max(avg, 1.0) * 100.0)
            .max()
            .orElse(0.0);

        System.out.printf("   Max deviation from average: %.1f%%%n", maxDev);
        System.out.printf("   Metrics: lookups=%d rebalance=%d nodes=%d vnodes=%d%n",
            ch.getMetrics().getLookups(),
            ch.getMetrics().getRebalanceCount(),
            ch.getNodeCount(),
            ch.getVirtualNodeCount());
    }
}
