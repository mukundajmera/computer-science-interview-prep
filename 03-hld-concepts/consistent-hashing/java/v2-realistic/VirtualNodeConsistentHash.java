import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * V2: Consistent Hash with Virtual Nodes
 * 
 * Improved consistent hashing with virtual nodes for better
 * load distribution. Each physical server is represented by
 * multiple points on the hash ring.
 * 
 * Features:
 * - Virtual nodes for even distribution
 * - MD5 hashing for better spread
 * - Configurable vnodes per server
 * - Server weighting support
 */
public class VirtualNodeConsistentHash {
    
    private final TreeMap<Long, String> ring;
    private final Map<String, Integer> serverWeights;
    private final int defaultVnodes;
    
    /**
     * Creates a consistent hash ring with virtual nodes.
     * 
     * @param defaultVnodes Default virtual nodes per server
     */
    public VirtualNodeConsistentHash(int defaultVnodes) {
        this.ring = new TreeMap<>();
        this.serverWeights = new HashMap<>();
        this.defaultVnodes = defaultVnodes;
    }
    
    /**
     * Adds a server with default weight.
     */
    public void addServer(String server) {
        addServer(server, 1);
    }
    
    /**
     * Adds a server with specified weight.
     * Higher weight = more virtual nodes = more keys.
     */
    public void addServer(String server, int weight) {
        if (serverWeights.containsKey(server)) {
            return;
        }
        
        serverWeights.put(server, weight);
        int vnodes = defaultVnodes * weight;
        
        for (int i = 0; i < vnodes; i++) {
            String vnodeKey = server + "#" + i;
            long hash = hash(vnodeKey);
            ring.put(hash, server);
        }
    }
    
    /**
     * Removes a server and all its virtual nodes.
     */
    public void removeServer(String server) {
        Integer weight = serverWeights.remove(server);
        if (weight == null) {
            return;
        }
        
        int vnodes = defaultVnodes * weight;
        for (int i = 0; i < vnodes; i++) {
            String vnodeKey = server + "#" + i;
            long hash = hash(vnodeKey);
            ring.remove(hash);
        }
    }
    
    /**
     * Gets the server responsible for the given key.
     */
    public String getServer(String key) {
        if (ring.isEmpty()) {
            return null;
        }
        
        long hash = hash(key);
        
        Map.Entry<Long, String> entry = ring.ceilingEntry(hash);
        if (entry == null) {
            entry = ring.firstEntry();
        }
        
        return entry.getValue();
    }
    
    /**
     * Gets N distinct servers for replication.
     */
    public List<String> getServers(String key, int count) {
        if (ring.isEmpty()) {
            return Collections.emptyList();
        }
        
        List<String> servers = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        
        long hash = hash(key);
        Long currentHash = hash;
        
        while (servers.size() < count && servers.size() < serverWeights.size()) {
            Map.Entry<Long, String> entry = ring.ceilingEntry(currentHash);
            if (entry == null) {
                entry = ring.firstEntry();
            }
            
            if (seen.add(entry.getValue())) {
                servers.add(entry.getValue());
            }
            
            currentHash = entry.getKey() + 1;
        }
        
        return servers;
    }
    
    /**
     * MD5-based hash function for better distribution.
     */
    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
            
            // Use first 8 bytes for long hash
            long hash = 0;
            for (int i = 0; i < 8; i++) {
                hash = (hash << 8) | (digest[i] & 0xFF);
            }
            return hash;
        } catch (NoSuchAlgorithmException e) {
            return key.hashCode();
        }
    }
    
    /**
     * Returns the total number of virtual nodes.
     */
    public int getVirtualNodeCount() {
        return ring.size();
    }
    
    /**
     * Returns the number of physical servers.
     */
    public int getServerCount() {
        return serverWeights.size();
    }
    
    /**
     * Returns all physical servers.
     */
    public Set<String> getServers() {
        return new HashSet<>(serverWeights.keySet());
    }
}
