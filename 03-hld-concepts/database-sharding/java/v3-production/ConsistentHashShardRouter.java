package v3_production;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Production-grade sharding with consistent hashing for dynamic shard management.
 * Supports adding/removing shards with minimal data movement.
 */
public class ConsistentHashShardRouter {

    private final TreeMap<Long, VirtualNode> ring;
    private final Map<String, ShardDatabase> shards;
    private final Map<String, List<Long>> shardToVnodes;
    private final int virtualNodesPerShard;
    private final int replicationFactor;
    private final ReadWriteLock lock;

    public ConsistentHashShardRouter(int virtualNodesPerShard, int replicationFactor) {
        this.ring = new TreeMap<>();
        this.shards = new ConcurrentHashMap<>();
        this.shardToVnodes = new ConcurrentHashMap<>();
        this.virtualNodesPerShard = virtualNodesPerShard;
        this.replicationFactor = replicationFactor;
        this.lock = new ReentrantReadWriteLock();
    }

    /**
     * Virtual node on the hash ring.
     */
    public static class VirtualNode {
        final String shardId;
        final int vnodeIndex;
        final long position;

        public VirtualNode(String shardId, int vnodeIndex, long position) {
            this.shardId = shardId;
            this.vnodeIndex = vnodeIndex;
            this.position = position;
        }
    }

    /**
     * Simulated shard database with replication support.
     */
    public static class ShardDatabase {
        private final String shardId;
        private final Map<String, Map<String, Object>> data;
        private boolean isHealthy;
        private long lastHealthCheck;

        public ShardDatabase(String shardId) {
            this.shardId = shardId;
            this.data = new ConcurrentHashMap<>();
            this.isHealthy = true;
            this.lastHealthCheck = System.currentTimeMillis();
        }

        public void put(String key, Map<String, Object> value) {
            data.put(key, value);
        }

        public Map<String, Object> get(String key) {
            return data.get(key);
        }

        public boolean delete(String key) {
            return data.remove(key) != null;
        }

        public int size() {
            return data.size();
        }

        public String getShardId() {
            return shardId;
        }

        public boolean isHealthy() {
            return isHealthy;
        }

        public void setHealthy(boolean healthy) {
            this.isHealthy = healthy;
            this.lastHealthCheck = System.currentTimeMillis();
        }

        public Map<String, Map<String, Object>> getAllData() {
            return new HashMap<>(data);
        }
    }

    /**
     * Add a new shard to the cluster.
     */
    public void addShard(String shardId) {
        lock.writeLock().lock();
        try {
            if (shards.containsKey(shardId)) {
                throw new IllegalArgumentException("Shard already exists: " + shardId);
            }

            shards.put(shardId, new ShardDatabase(shardId));
            List<Long> vnodePositions = new ArrayList<>();

            // Add virtual nodes
            for (int i = 0; i < virtualNodesPerShard; i++) {
                long position = hash(shardId + "#" + i);
                ring.put(position, new VirtualNode(shardId, i, position));
                vnodePositions.add(position);
            }
            
            shardToVnodes.put(shardId, vnodePositions);
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Remove a shard from the cluster (triggers data migration).
     */
    public Map<String, Map<String, Object>> removeShard(String shardId) {
        lock.writeLock().lock();
        try {
            if (!shards.containsKey(shardId)) {
                throw new IllegalArgumentException("Shard not found: " + shardId);
            }

            // Get data to migrate
            ShardDatabase shard = shards.get(shardId);
            Map<String, Map<String, Object>> dataToMigrate = shard.getAllData();

            // Remove virtual nodes
            List<Long> positions = shardToVnodes.remove(shardId);
            if (positions != null) {
                for (Long pos : positions) {
                    ring.remove(pos);
                }
            }

            shards.remove(shardId);
            return dataToMigrate;
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Get the primary shard for a key.
     */
    public String getShardForKey(String key) {
        lock.readLock().lock();
        try {
            if (ring.isEmpty()) {
                throw new IllegalStateException("No shards available");
            }

            long hash = hash(key);
            Map.Entry<Long, VirtualNode> entry = ring.ceilingEntry(hash);
            if (entry == null) {
                entry = ring.firstEntry();
            }
            return entry.getValue().shardId;
        } finally {
            lock.readLock().unlock();
        }
    }

    /**
     * Get shards for replication (N distinct shards).
     */
    public List<String> getShardsForReplication(String key) {
        lock.readLock().lock();
        try {
            if (ring.isEmpty()) {
                return Collections.emptyList();
            }

            Set<String> replicaShards = new LinkedHashSet<>();
            long hash = hash(key);

            // Start from the first node >= hash
            Map.Entry<Long, VirtualNode> entry = ring.ceilingEntry(hash);
            if (entry == null) {
                entry = ring.firstEntry();
            }

            // Collect unique shards until we have enough or exhausted
            Long startPos = entry.getKey();
            boolean wrapped = false;

            while (replicaShards.size() < replicationFactor && replicaShards.size() < shards.size()) {
                String shardId = entry.getValue().shardId;
                ShardDatabase shard = shards.get(shardId);
                
                if (shard != null && shard.isHealthy()) {
                    replicaShards.add(shardId);
                }

                entry = ring.higherEntry(entry.getKey());
                if (entry == null) {
                    entry = ring.firstEntry();
                    wrapped = true;
                }

                if (wrapped && entry.getKey().equals(startPos)) {
                    break;
                }
            }

            return new ArrayList<>(replicaShards);
        } finally {
            lock.readLock().unlock();
        }
    }

    /**
     * Store data with replication.
     */
    public void put(String key, Map<String, Object> value) {
        List<String> replicaShards = getShardsForReplication(key);
        if (replicaShards.isEmpty()) {
            throw new IllegalStateException("No healthy shards available");
        }

        for (String shardId : replicaShards) {
            shards.get(shardId).put(key, value);
        }
    }

    /**
     * Retrieve data (from primary or any healthy replica).
     */
    public Map<String, Object> get(String key) {
        List<String> replicaShards = getShardsForReplication(key);
        
        for (String shardId : replicaShards) {
            ShardDatabase shard = shards.get(shardId);
            if (shard != null && shard.isHealthy()) {
                Map<String, Object> value = shard.get(key);
                if (value != null) {
                    return value;
                }
            }
        }
        
        return null;
    }

    /**
     * Mark a shard as unhealthy.
     */
    public void markShardUnhealthy(String shardId) {
        ShardDatabase shard = shards.get(shardId);
        if (shard != null) {
            shard.setHealthy(false);
        }
    }

    /**
     * Mark a shard as healthy.
     */
    public void markShardHealthy(String shardId) {
        ShardDatabase shard = shards.get(shardId);
        if (shard != null) {
            shard.setHealthy(true);
        }
    }

    /**
     * Print distribution statistics.
     */
    public void printDistribution() {
        System.out.println("=== Shard Distribution ===");
        int totalItems = shards.values().stream().mapToInt(ShardDatabase::size).sum();
        
        for (Map.Entry<String, ShardDatabase> entry : shards.entrySet()) {
            ShardDatabase shard = entry.getValue();
            String status = shard.isHealthy() ? "healthy" : "unhealthy";
            int percentage = totalItems > 0 ? (shard.size() * 100) / totalItems : 0;
            System.out.printf("Shard %s: %d items (%d%%) [%s]%n",
                    entry.getKey(), shard.size(), percentage, status);
        }
    }

    /**
     * Calculate hash for a key.
     */
    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes());
            return ((long) (digest[0] & 0xFF) << 24) |
                   ((long) (digest[1] & 0xFF) << 16) |
                   ((long) (digest[2] & 0xFF) << 8) |
                   ((long) (digest[3] & 0xFF));
        } catch (NoSuchAlgorithmException e) {
            return key.hashCode() & 0xFFFFFFFFL;
        }
    }

    public int getShardCount() {
        return shards.size();
    }

    public int getVirtualNodeCount() {
        return ring.size();
    }
}
