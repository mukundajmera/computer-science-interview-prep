package v1_simple;

import java.util.HashMap;
import java.util.Map;

/**
 * Simple hash-based database sharding implementation.
 * Demonstrates the basic concept of distributing data across shards
 * using modulo hashing.
 */
public class HashShardRouter {
    private final int numShards;
    private final Map<Integer, Map<String, String>> shards;

    public HashShardRouter(int numShards) {
        this.numShards = numShards;
        this.shards = new HashMap<>();
        
        // Initialize empty shards
        for (int i = 0; i < numShards; i++) {
            shards.put(i, new HashMap<>());
        }
    }

    /**
     * Calculate which shard should store data for given key.
     */
    public int getShardId(String shardKey) {
        int hash = Math.abs(shardKey.hashCode());
        return hash % numShards;
    }

    /**
     * Store data in the appropriate shard.
     */
    public void put(String shardKey, String key, String value) {
        int shardId = getShardId(shardKey);
        shards.get(shardId).put(key, value);
    }

    /**
     * Retrieve data from the appropriate shard.
     */
    public String get(String shardKey, String key) {
        int shardId = getShardId(shardKey);
        return shards.get(shardId).get(key);
    }

    /**
     * Delete data from the appropriate shard.
     */
    public boolean delete(String shardKey, String key) {
        int shardId = getShardId(shardKey);
        return shards.get(shardId).remove(key) != null;
    }

    /**
     * Get the size of a specific shard.
     */
    public int getShardSize(int shardId) {
        return shards.get(shardId).size();
    }

    /**
     * Get total number of items across all shards.
     */
    public int getTotalSize() {
        return shards.values().stream()
                .mapToInt(Map::size)
                .sum();
    }

    /**
     * Print distribution statistics.
     */
    public void printDistribution() {
        System.out.println("=== Shard Distribution ===");
        for (int i = 0; i < numShards; i++) {
            int size = shards.get(i).size();
            int percentage = getTotalSize() > 0 ? (size * 100) / getTotalSize() : 0;
            System.out.printf("Shard %d: %d items (%d%%)%n", i, size, percentage);
        }
    }

    public int getNumShards() {
        return numShards;
    }
}
