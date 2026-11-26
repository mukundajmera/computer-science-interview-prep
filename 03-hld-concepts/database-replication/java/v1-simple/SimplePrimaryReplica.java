/**
 * V1: Simple Primary-Replica Simulation
 * 
 * Basic simulation of master-slave replication with
 * write/read separation.
 * 
 * Features:
 * - Single primary for writes
 * - Multiple replicas for reads
 * - Simple synchronous replication
 */

package v1_simple;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class SimplePrimaryReplica {
    
    private final Database primary;
    private final List<Database> replicas;
    
    public SimplePrimaryReplica(int replicaCount) {
        this.primary = new Database("primary");
        this.replicas = new ArrayList<>();
        
        for (int i = 0; i < replicaCount; i++) {
            replicas.add(new Database("replica-" + i));
        }
    }
    
    /**
     * Writes to primary and replicates to all replicas.
     */
    public void write(String key, String value) {
        // Write to primary
        primary.put(key, value);
        System.out.println("[PRIMARY] Write: " + key + " = " + value);
        
        // Replicate to all replicas (synchronous)
        for (Database replica : replicas) {
            replica.put(key, value);
            System.out.println("[" + replica.name + "] Replicated: " + key);
        }
    }
    
    /**
     * Reads from a replica (round-robin).
     */
    public String read(String key) {
        if (replicas.isEmpty()) {
            return primary.get(key);
        }
        
        // Simple round-robin selection
        int index = Math.abs(key.hashCode()) % replicas.size();
        Database replica = replicas.get(index);
        
        String value = replica.get(key);
        System.out.println("[" + replica.name + "] Read: " + key + " = " + value);
        return value;
    }
    
    /**
     * Reads from primary (for read-your-writes consistency).
     */
    public String readFromPrimary(String key) {
        String value = primary.get(key);
        System.out.println("[PRIMARY] Read: " + key + " = " + value);
        return value;
    }
    
    public void printStatus() {
        System.out.println("\n=== Database Status ===");
        System.out.println("Primary: " + primary.size() + " records");
        for (Database replica : replicas) {
            System.out.println(replica.name + ": " + replica.size() + " records");
        }
    }
    
    /**
     * Simple in-memory database.
     */
    static class Database {
        final String name;
        private final Map<String, String> data = new HashMap<>();
        
        Database(String name) {
            this.name = name;
        }
        
        void put(String key, String value) {
            data.put(key, value);
        }
        
        String get(String key) {
            return data.get(key);
        }
        
        int size() {
            return data.size();
        }
    }
}
