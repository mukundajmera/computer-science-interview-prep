/**
 * V2: Async Replication with Lag Simulation
 * 
 * Demonstrates asynchronous replication with configurable lag
 * and read routing based on consistency requirements.
 * 
 * Features:
 * - Asynchronous replication
 * - Simulated replication lag
 * - Read-your-writes consistency option
 * - Lag monitoring
 */

package v2_realistic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;

public class AsyncReplication {
    
    private final Database primary;
    private final List<ReplicaDatabase> replicas;
    private final ExecutorService replicationExecutor;
    private final Map<String, Long> writeTimestamps = new ConcurrentHashMap<>();
    private int roundRobinIndex = 0;
    
    public AsyncReplication(int replicaCount, long replicationDelayMs) {
        this.primary = new Database("primary");
        this.replicas = new ArrayList<>();
        this.replicationExecutor = Executors.newFixedThreadPool(replicaCount);
        
        for (int i = 0; i < replicaCount; i++) {
            replicas.add(new ReplicaDatabase("replica-" + i, replicationDelayMs));
        }
    }
    
    /**
     * Writes to primary and asynchronously replicates.
     */
    public void write(String key, String value) {
        long timestamp = System.currentTimeMillis();
        
        // Write to primary immediately
        primary.put(key, value, timestamp);
        writeTimestamps.put(key, timestamp);
        System.out.println("[PRIMARY] Write: " + key + " = " + value);
        
        // Async replication to all replicas
        for (ReplicaDatabase replica : replicas) {
            replicationExecutor.submit(() -> {
                replica.replicateWithDelay(key, value, timestamp);
            });
        }
    }
    
    /**
     * Reads with eventual consistency (from any replica).
     */
    public String readEventual(String key) {
        if (replicas.isEmpty()) {
            return primary.get(key);
        }
        
        ReplicaDatabase replica = replicas.get(roundRobinIndex++ % replicas.size());
        String value = replica.get(key);
        System.out.printf("[%s] Read (eventual): %s = %s (lag: %dms)%n",
                         replica.name, key, value, replica.getCurrentLag());
        return value;
    }
    
    /**
     * Reads with read-your-writes consistency.
     */
    public String readConsistent(String key) {
        Long writeTime = writeTimestamps.get(key);
        
        if (writeTime == null) {
            return readEventual(key);
        }
        
        // Check if any replica is caught up
        for (ReplicaDatabase replica : replicas) {
            if (replica.getLastAppliedTime(key) >= writeTime) {
                String value = replica.get(key);
                System.out.printf("[%s] Read (consistent): %s = %s%n",
                                 replica.name, key, value);
                return value;
            }
        }
        
        // Fall back to primary
        String value = primary.get(key);
        System.out.printf("[PRIMARY] Read (consistent, fallback): %s = %s%n", key, value);
        return value;
    }
    
    public void printLagStatus() {
        System.out.println("\n=== Replication Lag Status ===");
        for (ReplicaDatabase replica : replicas) {
            System.out.printf("%s: lag=%dms%n", replica.name, replica.getCurrentLag());
        }
    }
    
    public void shutdown() {
        replicationExecutor.shutdown();
    }
    
    /**
     * Primary database with timestamps.
     */
    static class Database {
        final String name;
        private final Map<String, Entry> data = new ConcurrentHashMap<>();
        
        Database(String name) {
            this.name = name;
        }
        
        void put(String key, String value, long timestamp) {
            data.put(key, new Entry(value, timestamp));
        }
        
        String get(String key) {
            Entry entry = data.get(key);
            return entry != null ? entry.value : null;
        }
        
        static class Entry {
            final String value;
            final long timestamp;
            
            Entry(String value, long timestamp) {
                this.value = value;
                this.timestamp = timestamp;
            }
        }
    }
    
    /**
     * Replica with simulated lag.
     */
    static class ReplicaDatabase {
        final String name;
        private final long replicationDelayMs;
        private final Map<String, Entry> data = new ConcurrentHashMap<>();
        private volatile long lastReplicationTime = System.currentTimeMillis();
        
        ReplicaDatabase(String name, long replicationDelayMs) {
            this.name = name;
            this.replicationDelayMs = replicationDelayMs;
        }
        
        void replicateWithDelay(String key, String value, long timestamp) {
            try {
                Thread.sleep(replicationDelayMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
            
            data.put(key, new Entry(value, timestamp));
            lastReplicationTime = System.currentTimeMillis();
            System.out.printf("[%s] Replicated: %s (delay: %dms)%n",
                             name, key, replicationDelayMs);
        }
        
        String get(String key) {
            Entry entry = data.get(key);
            return entry != null ? entry.value : null;
        }
        
        long getLastAppliedTime(String key) {
            Entry entry = data.get(key);
            return entry != null ? entry.timestamp : 0;
        }
        
        long getCurrentLag() {
            return System.currentTimeMillis() - lastReplicationTime;
        }
        
        static class Entry {
            final String value;
            final long timestamp;
            
            Entry(String value, long timestamp) {
                this.value = value;
                this.timestamp = timestamp;
            }
        }
    }
}
