import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/**
 * V3: Production Consistent Hashing with Replication
 * 
 * A production-ready consistent hashing implementation featuring:
 * - Virtual nodes with configurable count
 * - Replication factor support
 * - Bounded load balancing
 * - Node health tracking
 * - Metrics collection
 * 
 * This demonstrates patterns used in systems like Cassandra,
 * DynamoDB, and distributed caches.
 */
public class ProductionConsistentHash {
    
    private final TreeMap<Long, String> ring;
    private final Map<String, NodeInfo> nodes;
    private final int defaultVnodes;
    private final int replicationFactor;
    private final double loadFactor;  // For bounded load
    private final Metrics metrics;
    
    /**
     * Node information including health and load.
     */
    public static class NodeInfo {
        private final String nodeId;
        private final int weight;
        private volatile boolean healthy = true;
        private final AtomicLong requestCount = new AtomicLong(0);
        private final AtomicLong keyCount = new AtomicLong(0);
        
        public NodeInfo(String nodeId, int weight) {
            this.nodeId = nodeId;
            this.weight = weight;
        }
        
        public String getNodeId() { return nodeId; }
        public int getWeight() { return weight; }
        public boolean isHealthy() { return healthy; }
        public long getRequestCount() { return requestCount.get(); }
        public long getKeyCount() { return keyCount.get(); }
        
        void setHealthy(boolean healthy) { this.healthy = healthy; }
        void incrementRequests() { requestCount.incrementAndGet(); }
        void incrementKeys() { keyCount.incrementAndGet(); }
        void decrementKeys() { keyCount.decrementAndGet(); }
    }
    
    /**
     * Metrics for the hash ring.
     */
    public static class Metrics {
        private final AtomicLong lookups = new AtomicLong(0);
        private final AtomicLong rebalanceCount = new AtomicLong(0);
        
        void recordLookup() { lookups.incrementAndGet(); }
        void recordRebalance() { rebalanceCount.incrementAndGet(); }
        
        public long getLookups() { return lookups.get(); }
        public long getRebalanceCount() { return rebalanceCount.get(); }
    }
    
    /**
     * Result of a key lookup with replica information.
     */
    public static class LookupResult {
        private final String primaryNode;
        private final List<String> replicas;
        
        public LookupResult(String primaryNode, List<String> replicas) {
            this.primaryNode = primaryNode;
            this.replicas = replicas;
        }
        
        public String getPrimaryNode() { return primaryNode; }
        public List<String> getReplicas() { return replicas; }
        public List<String> getAllNodes() {
            List<String> all = new ArrayList<>();
            all.add(primaryNode);
            all.addAll(replicas);
            return all;
        }
    }
    
    /**
     * Creates a production consistent hash ring.
     * 
     * @param defaultVnodes Virtual nodes per unit weight
     * @param replicationFactor Number of replica copies
     * @param loadFactor Max load factor for bounded load (1.0 = disabled)
     */
    public ProductionConsistentHash(int defaultVnodes, int replicationFactor, double loadFactor) {
        this.ring = new TreeMap<>();
        this.nodes = new ConcurrentHashMap<>();
        this.defaultVnodes = defaultVnodes;
        this.replicationFactor = replicationFactor;
        this.loadFactor = loadFactor;
        this.metrics = new Metrics();
    }
    
    /**
     * Adds a node with default weight.
     */
    public synchronized void addNode(String nodeId) {
        addNode(nodeId, 1);
    }
    
    /**
     * Adds a node with specified weight.
     */
    public synchronized void addNode(String nodeId, int weight) {
        if (nodes.containsKey(nodeId)) {
            return;
        }
        
        NodeInfo info = new NodeInfo(nodeId, weight);
        nodes.put(nodeId, info);
        
        int vnodes = defaultVnodes * weight;
        for (int i = 0; i < vnodes; i++) {
            long hash = hash(nodeId + "#" + i);
            ring.put(hash, nodeId);
        }
        
        metrics.recordRebalance();
    }
    
    /**
     * Removes a node from the ring.
     */
    public synchronized void removeNode(String nodeId) {
        NodeInfo info = nodes.remove(nodeId);
        if (info == null) {
            return;
        }
        
        int vnodes = defaultVnodes * info.getWeight();
        for (int i = 0; i < vnodes; i++) {
            long hash = hash(nodeId + "#" + i);
            ring.remove(hash);
        }
        
        metrics.recordRebalance();
    }
    
    /**
     * Sets node health status.
     */
    public void setNodeHealth(String nodeId, boolean healthy) {
        NodeInfo info = nodes.get(nodeId);
        if (info != null) {
            info.setHealthy(healthy);
        }
    }
    
    /**
     * Looks up the primary and replica nodes for a key.
     */
    public LookupResult lookup(String key) {
        metrics.recordLookup();
        
        if (ring.isEmpty()) {
            return null;
        }
        
        List<String> nodeList = getNodesForKey(key, replicationFactor);
        if (nodeList.isEmpty()) {
            return null;
        }
        
        String primary = nodeList.get(0);
        List<String> replicas = nodeList.size() > 1 
            ? nodeList.subList(1, nodeList.size()) 
            : Collections.emptyList();
        
        return new LookupResult(primary, new ArrayList<>(replicas));
    }
    
    /**
     * Gets N distinct healthy nodes for a key.
     */
    private List<String> getNodesForKey(String key, int count) {
        List<String> result = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        
        long hash = hash(key);
        Long currentHash = hash;
        int attempts = 0;
        int maxAttempts = ring.size();
        
        while (result.size() < count && result.size() < nodes.size() && attempts < maxAttempts) {
            Map.Entry<Long, String> entry = ring.ceilingEntry(currentHash);
            if (entry == null) {
                entry = ring.firstEntry();
            }
            
            String nodeId = entry.getValue();
            NodeInfo info = nodes.get(nodeId);
            
            // Skip if already seen or unhealthy
            if (!seen.contains(nodeId) && info != null && info.isHealthy()) {
                // Bounded load check
                if (loadFactor == 1.0 || checkBoundedLoad(info)) {
                    seen.add(nodeId);
                    result.add(nodeId);
                    info.incrementRequests();
                }
            }
            
            currentHash = entry.getKey() + 1;
            attempts++;
        }
        
        return result;
    }
    
    /**
     * Checks if node is within bounded load limits.
     */
    private boolean checkBoundedLoad(NodeInfo node) {
        if (loadFactor <= 1.0) {
            return true;
        }
        
        long totalRequests = nodes.values().stream()
            .mapToLong(NodeInfo::getRequestCount)
            .sum();
        
        double avgLoad = (double) totalRequests / nodes.size();
        double maxLoad = avgLoad * loadFactor;
        
        return node.getRequestCount() < maxLoad;
    }
    
    /**
     * MD5-based hash function.
     */
    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
            
            long hash = 0;
            for (int i = 0; i < 8; i++) {
                hash = (hash << 8) | (digest[i] & 0xFF);
            }
            return hash;
        } catch (Exception e) {
            return key.hashCode();
        }
    }
    
    /**
     * Returns statistics about key distribution.
     */
    public Map<String, Long> getDistribution() {
        Map<String, Long> dist = new HashMap<>();
        nodes.forEach((id, info) -> dist.put(id, info.getRequestCount()));
        return dist;
    }
    
    /**
     * Returns all node information.
     */
    public Collection<NodeInfo> getNodes() {
        return Collections.unmodifiableCollection(nodes.values());
    }
    
    public int getNodeCount() {
        return nodes.size();
    }
    
    public int getVirtualNodeCount() {
        return ring.size();
    }
    
    public Metrics getMetrics() {
        return metrics;
    }
}
