package v2_realistic;

import java.util.*;

/**
 * Range-based sharding with dynamic shard configuration.
 * More realistic implementation with range definitions and routing.
 */
public class RangeShardRouter {
    
    private final TreeMap<Long, ShardConfig> shardRanges;
    private final Map<String, ShardDatabase> shards;

    public RangeShardRouter() {
        this.shardRanges = new TreeMap<>();
        this.shards = new HashMap<>();
    }

    /**
     * Configuration for a single shard.
     */
    public static class ShardConfig {
        public final String shardId;
        final long startRange;
        final long endRange;
        boolean isHealthy;

        public ShardConfig(String shardId, long startRange, long endRange) {
            this.shardId = shardId;
            this.startRange = startRange;
            this.endRange = endRange;
            this.isHealthy = true;
        }

        public boolean contains(long value) {
            return value >= startRange && value < endRange;
        }
    }

    /**
     * Simple in-memory shard database.
     */
    public static class ShardDatabase {
        public final String shardId;
        private final Map<Long, Map<String, Object>> data;

        public ShardDatabase(String shardId) {
            this.shardId = shardId;
            this.data = new HashMap<>();
        }

        public void put(long key, Map<String, Object> value) {
            data.put(key, value);
        }

        public Map<String, Object> get(long key) {
            return data.get(key);
        }

        public List<Map<String, Object>> rangeQuery(long start, long end) {
            List<Map<String, Object>> results = new ArrayList<>();
            for (Map.Entry<Long, Map<String, Object>> entry : data.entrySet()) {
                if (entry.getKey() >= start && entry.getKey() < end) {
                    results.add(entry.getValue());
                }
            }
            return results;
        }

        public int size() {
            return data.size();
        }

        public String getShardId() {
            return shardId;
        }
    }

    /**
     * Add a shard with its range configuration.
     */
    public void addShard(String shardId, long startRange, long endRange) {
        ShardConfig config = new ShardConfig(shardId, startRange, endRange);
        shardRanges.put(startRange, config);
        shards.put(shardId, new ShardDatabase(shardId));
    }

    /**
     * Route a key to its shard.
     */
    public ShardConfig routeToShard(long key) {
        Map.Entry<Long, ShardConfig> entry = shardRanges.floorEntry(key);
        if (entry != null && entry.getValue().contains(key)) {
            return entry.getValue();
        }
        throw new IllegalArgumentException("No shard found for key: " + key);
    }

    /**
     * Store data in appropriate shard.
     */
    public void put(long key, Map<String, Object> value) {
        ShardConfig config = routeToShard(key);
        if (!config.isHealthy) {
            throw new RuntimeException("Shard " + config.shardId + " is unhealthy");
        }
        shards.get(config.shardId).put(key, value);
    }

    /**
     * Retrieve data from appropriate shard.
     */
    public Map<String, Object> get(long key) {
        ShardConfig config = routeToShard(key);
        return shards.get(config.shardId).get(key);
    }

    /**
     * Execute range query across relevant shards.
     */
    public List<Map<String, Object>> rangeQuery(long start, long end) {
        List<Map<String, Object>> results = new ArrayList<>();
        
        for (ShardConfig config : shardRanges.values()) {
            // Check if shard range overlaps with query range
            if (config.startRange < end && config.endRange > start) {
                ShardDatabase shard = shards.get(config.shardId);
                results.addAll(shard.rangeQuery(start, end));
            }
        }
        
        return results;
    }

    /**
     * Mark a shard as unhealthy.
     */
    public void markShardUnhealthy(String shardId) {
        for (ShardConfig config : shardRanges.values()) {
            if (config.shardId.equals(shardId)) {
                config.isHealthy = false;
                break;
            }
        }
    }

    /**
     * Print shard distribution.
     */
    public void printDistribution() {
        System.out.println("=== Shard Distribution ===");
        for (ShardConfig config : shardRanges.values()) {
            ShardDatabase shard = shards.get(config.shardId);
            String status = config.isHealthy ? "healthy" : "unhealthy";
            System.out.printf("Shard %s [%d-%d): %d items (%s)%n",
                    config.shardId, config.startRange, config.endRange,
                    shard.size(), status);
        }
    }

    public int getShardCount() {
        return shards.size();
    }
}
