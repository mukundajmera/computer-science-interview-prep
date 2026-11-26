import java.util.*;

/**
 * V1: Simple Consistent Hash Ring
 * 
 * Basic implementation of consistent hashing using a TreeMap
 * to represent the hash ring. Keys are assigned to the first
 * server found clockwise from their hash position.
 * 
 * Features:
 * - Simple hash ring implementation
 * - Add/remove servers dynamically
 * - O(log n) key lookup
 * 
 * Limitations:
 * - No virtual nodes (uneven distribution)
 * - Uses simple hashCode (not ideal for production)
 */
public class SimpleConsistentHash {
    
    private final TreeMap<Integer, String> ring;
    private final Set<String> servers;
    
    public SimpleConsistentHash() {
        this.ring = new TreeMap<>();
        this.servers = new HashSet<>();
    }
    
    /**
     * Adds a server to the ring.
     */
    public void addServer(String server) {
        if (servers.add(server)) {
            int hash = hash(server);
            ring.put(hash, server);
        }
    }
    
    /**
     * Removes a server from the ring.
     */
    public void removeServer(String server) {
        if (servers.remove(server)) {
            int hash = hash(server);
            ring.remove(hash);
        }
    }
    
    /**
     * Gets the server responsible for the given key.
     * Walks clockwise from key's hash position.
     */
    public String getServer(String key) {
        if (ring.isEmpty()) {
            return null;
        }
        
        int hash = hash(key);
        
        // Get the first server at or after this hash
        Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
        
        // If no server found (past the last one), wrap around
        if (entry == null) {
            entry = ring.firstEntry();
        }
        
        return entry.getValue();
    }
    
    /**
     * Simple hash function.
     */
    private int hash(String key) {
        return key.hashCode() & 0x7FFFFFFF;  // Ensure positive
    }
    
    /**
     * Returns all servers in the ring.
     */
    public Set<String> getServers() {
        return new HashSet<>(servers);
    }
    
    /**
     * Returns the number of servers.
     */
    public int getServerCount() {
        return servers.size();
    }
}
