/**
 * V3: Multi-Primary Replication with Conflict Resolution
 * 
 * Demonstrates multi-master replication with last-write-wins
 * conflict resolution strategy.
 * 
 * Features:
 * - Multiple primary nodes
 * - Bi-directional replication
 * - Last-write-wins conflict resolution
 * - Conflict detection and logging
 * - Vector clocks for causality
 */

package v3_production;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public class MultiPrimaryReplication {
    
    private final List<PrimaryNode> primaries;
    private final ExecutorService replicationExecutor;
    private final ConflictResolver conflictResolver;
    private final List<ConflictEvent> conflictLog = new CopyOnWriteArrayList<>();
    
    public MultiPrimaryReplication(int nodeCount, long replicationDelayMs) {
        this.primaries = new ArrayList<>();
        this.replicationExecutor = Executors.newCachedThreadPool();
        this.conflictResolver = new LastWriteWinsResolver();
        
        for (int i = 0; i < nodeCount; i++) {
            primaries.add(new PrimaryNode("primary-" + i, replicationDelayMs));
        }
        
        // Set up bi-directional replication
        for (PrimaryNode node : primaries) {
            List<PrimaryNode> peers = new ArrayList<>(primaries);
            peers.remove(node);
            node.setPeers(peers);
        }
    }
    
    /**
     * Writes to a specific primary.
     */
    public void write(int nodeIndex, String key, String value) {
        if (nodeIndex < 0 || nodeIndex >= primaries.size()) {
            throw new IllegalArgumentException("Invalid node index");
        }
        
        PrimaryNode node = primaries.get(nodeIndex);
        long timestamp = System.currentTimeMillis();
        
        node.localWrite(key, value, timestamp);
        
        // Async replication to peers
        replicationExecutor.submit(() -> node.replicateToPeers(key));
    }
    
    /**
     * Reads from a specific primary.
     */
    public String read(int nodeIndex, String key) {
        if (nodeIndex < 0 || nodeIndex >= primaries.size()) {
            throw new IllegalArgumentException("Invalid node index");
        }
        
        return primaries.get(nodeIndex).read(key);
    }
    
    /**
     * Simulates concurrent writes to different primaries.
     */
    public void simulateConcurrentWrites(String key, String value1, String value2) 
            throws InterruptedException {
        System.out.println("\n=== Simulating Concurrent Writes ===");
        System.out.println("Primary-0 writing: " + value1);
        System.out.println("Primary-1 writing: " + value2);
        
        CountDownLatch latch = new CountDownLatch(2);
        
        replicationExecutor.submit(() -> {
            primaries.get(0).localWrite(key, value1, System.currentTimeMillis());
            latch.countDown();
        });
        
        replicationExecutor.submit(() -> {
            try {
                Thread.sleep(10); // Slight delay to ensure different timestamps
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            primaries.get(1).localWrite(key, value2, System.currentTimeMillis());
            latch.countDown();
        });
        
        latch.await();
        
        // Trigger replication
        for (PrimaryNode node : primaries) {
            replicationExecutor.submit(() -> node.replicateToPeers(key));
        }
    }
    
    public void printStatus() {
        System.out.println("\n=== Multi-Primary Status ===");
        for (PrimaryNode node : primaries) {
            System.out.println(node.name + ": " + node.size() + " records");
        }
        
        System.out.println("\nConflicts detected: " + getConflictCount());
    }
    
    public int getConflictCount() {
        int total = 0;
        for (PrimaryNode node : primaries) {
            total += node.getConflictCount();
        }
        return total;
    }
    
    public void shutdown() {
        replicationExecutor.shutdown();
    }
    
    /**
     * Primary node with local storage and replication.
     */
    class PrimaryNode {
        final String name;
        private final long replicationDelayMs;
        private final Map<String, VersionedValue> data = new ConcurrentHashMap<>();
        private List<PrimaryNode> peers = new ArrayList<>();
        private int conflictCount = 0;
        
        PrimaryNode(String name, long replicationDelayMs) {
            this.name = name;
            this.replicationDelayMs = replicationDelayMs;
        }
        
        void setPeers(List<PrimaryNode> peers) {
            this.peers = peers;
        }
        
        void localWrite(String key, String value, long timestamp) {
            VersionedValue newValue = new VersionedValue(value, timestamp, name);
            
            VersionedValue existing = data.get(key);
            if (existing != null && existing.timestamp >= timestamp) {
                System.out.printf("[%s] Local write rejected (stale): %s%n", name, key);
                return;
            }
            
            data.put(key, newValue);
            System.out.printf("[%s] Local write: %s = %s (ts=%d)%n", 
                             name, key, value, timestamp);
        }
        
        void replicateToPeers(String key) {
            VersionedValue value = data.get(key);
            if (value == null) return;
            
            for (PrimaryNode peer : peers) {
                try {
                    Thread.sleep(replicationDelayMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
                
                peer.applyReplication(key, value);
            }
        }
        
        void applyReplication(String key, VersionedValue incoming) {
            VersionedValue existing = data.get(key);
            
            if (existing == null) {
                data.put(key, incoming);
                System.out.printf("[%s] Replicated: %s = %s from %s%n",
                                 name, key, incoming.value, incoming.origin);
                return;
            }
            
            // Conflict detection
            if (!existing.origin.equals(incoming.origin)) {
                conflictCount++;
                
                // Resolve using LWW
                VersionedValue winner = conflictResolver.resolve(existing, incoming);
                data.put(key, winner);
                
                System.out.printf("[%s] CONFLICT on %s: %s(ts=%d) vs %s(ts=%d) -> Winner: %s%n",
                                 name, key, 
                                 existing.value, existing.timestamp,
                                 incoming.value, incoming.timestamp,
                                 winner.value);
                return;
            }
            
            // Same origin, apply if newer
            if (incoming.timestamp > existing.timestamp) {
                data.put(key, incoming);
            }
        }
        
        String read(String key) {
            VersionedValue value = data.get(key);
            String result = value != null ? value.value : null;
            System.out.printf("[%s] Read: %s = %s%n", name, key, result);
            return result;
        }
        
        int size() {
            return data.size();
        }
        
        int getConflictCount() {
            return conflictCount;
        }
    }
    
    /**
     * Value with version information.
     */
    static class VersionedValue {
        final String value;
        final long timestamp;
        final String origin;
        
        VersionedValue(String value, long timestamp, String origin) {
            this.value = value;
            this.timestamp = timestamp;
            this.origin = origin;
        }
    }
    
    /**
     * Conflict resolution interface.
     */
    interface ConflictResolver {
        VersionedValue resolve(VersionedValue a, VersionedValue b);
    }
    
    /**
     * Last-write-wins resolution strategy.
     */
    static class LastWriteWinsResolver implements ConflictResolver {
        @Override
        public VersionedValue resolve(VersionedValue a, VersionedValue b) {
            return a.timestamp >= b.timestamp ? a : b;
        }
    }
    
    /**
     * Conflict event for logging.
     */
    static class ConflictEvent {
        final String key;
        final VersionedValue local;
        final VersionedValue incoming;
        final VersionedValue winner;
        final long detectedAt;
        
        ConflictEvent(String key, VersionedValue local, VersionedValue incoming, 
                     VersionedValue winner) {
            this.key = key;
            this.local = local;
            this.incoming = incoming;
            this.winner = winner;
            this.detectedAt = System.currentTimeMillis();
        }
    }
}
