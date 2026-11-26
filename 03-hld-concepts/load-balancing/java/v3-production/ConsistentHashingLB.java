package v3_production;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;

/**
 * V3: Production Load Balancer with Consistent Hashing
 * 
 * A production-ready load balancer featuring:
 * - Multiple load balancing algorithms
 * - Consistent hashing for sticky sessions
 * - Virtual nodes for even distribution
 * - Health checking with circuit breaker
 * - Connection tracking
 * - Comprehensive metrics
 * 
 * This demonstrates patterns used in production systems like
 * Nginx, HAProxy, and cloud load balancers.
 */
public class ConsistentHashingLB {
    
    // Consistent hash ring
    private final TreeMap<Long, String> hashRing = new TreeMap<>();
    private final Map<String, ServerNode> serverNodes = new ConcurrentHashMap<>();
    private final int virtualNodes;
    
    // Connection tracking for least connections algorithm
    private final Map<String, AtomicInteger> activeConnections = new ConcurrentHashMap<>();
    
    // Health checking
    private final ScheduledExecutorService scheduler;
    private final HealthCheckConfig healthConfig;
    
    // Metrics
    private final Metrics metrics = new Metrics();
    
    // Algorithm selection
    private volatile Algorithm algorithm = Algorithm.CONSISTENT_HASH;
    
    public enum Algorithm {
        ROUND_ROBIN,
        LEAST_CONNECTIONS,
        CONSISTENT_HASH,
        RANDOM
    }
    
    /**
     * Server node with metadata.
     */
    public static class ServerNode {
        private final String address;
        private final int weight;
        private volatile boolean healthy = true;
        private final AtomicInteger failureCount = new AtomicInteger(0);
        private final AtomicInteger successCount = new AtomicInteger(0);
        private volatile long lastResponseTime = 0;
        private final AtomicLong totalRequests = new AtomicLong(0);
        
        public ServerNode(String address, int weight) {
            this.address = address;
            this.weight = weight;
        }
        
        public String getAddress() { return address; }
        public int getWeight() { return weight; }
        public boolean isHealthy() { return healthy; }
        public long getTotalRequests() { return totalRequests.get(); }
        
        void markHealthy() {
            this.healthy = true;
            this.failureCount.set(0);
        }
        
        void markUnhealthy() {
            this.healthy = false;
        }
        
        void recordSuccess(long responseTimeMs) {
            successCount.incrementAndGet();
            failureCount.set(0);
            lastResponseTime = responseTimeMs;
        }
        
        void recordFailure() {
            failureCount.incrementAndGet();
        }
        
        int getFailureCount() { return failureCount.get(); }
        long getLastResponseTime() { return lastResponseTime; }
    }
    
    /**
     * Health check configuration.
     */
    public static class HealthCheckConfig {
        public int intervalMs = 5000;
        public int timeoutMs = 2000;
        public int unhealthyThreshold = 3;
        public int healthyThreshold = 2;
        public HealthChecker checker = (addr, timeout) -> true;
    }
    
    @FunctionalInterface
    public interface HealthChecker {
        boolean check(String address, int timeoutMs);
    }
    
    /**
     * Metrics tracking.
     */
    public static class Metrics {
        private final AtomicLong totalRequests = new AtomicLong(0);
        private final AtomicLong failedRequests = new AtomicLong(0);
        private final Map<String, AtomicLong> serverRequests = new ConcurrentHashMap<>();
        
        void recordRequest(String server, boolean success) {
            totalRequests.incrementAndGet();
            if (!success) failedRequests.incrementAndGet();
            serverRequests.computeIfAbsent(server, k -> new AtomicLong()).incrementAndGet();
        }
        
        public long getTotalRequests() { return totalRequests.get(); }
        public long getFailedRequests() { return failedRequests.get(); }
        
        public double getSuccessRate() {
            long total = totalRequests.get();
            return total == 0 ? 100.0 : 
                (total - failedRequests.get()) * 100.0 / total;
        }
        
        public Map<String, Long> getDistribution() {
            Map<String, Long> dist = new HashMap<>();
            serverRequests.forEach((k, v) -> dist.put(k, v.get()));
            return dist;
        }
    }
    
    /**
     * Creates a consistent hashing load balancer.
     * 
     * @param virtualNodesPerServer Number of virtual nodes per physical server
     * @param healthConfig Health check configuration
     */
    public ConsistentHashingLB(int virtualNodesPerServer, HealthCheckConfig healthConfig) {
        this.virtualNodes = virtualNodesPerServer;
        this.healthConfig = healthConfig;
        
        this.scheduler = Executors.newScheduledThreadPool(2, r -> {
            Thread t = new Thread(r, "lb-health-checker");
            t.setDaemon(true);
            return t;
        });
        
        // Start health checking
        scheduler.scheduleAtFixedRate(
            this::performHealthChecks,
            healthConfig.intervalMs,
            healthConfig.intervalMs,
            TimeUnit.MILLISECONDS
        );
    }
    
    /**
     * Adds a server to the load balancer.
     */
    public synchronized void addServer(String address, int weight) {
        ServerNode node = new ServerNode(address, weight);
        serverNodes.put(address, node);
        activeConnections.put(address, new AtomicInteger(0));
        
        // Add virtual nodes to hash ring
        for (int i = 0; i < virtualNodes * weight; i++) {
            long hash = hash(address + "#" + i);
            hashRing.put(hash, address);
        }
    }
    
    /**
     * Removes a server from the load balancer.
     */
    public synchronized void removeServer(String address) {
        serverNodes.remove(address);
        activeConnections.remove(address);
        
        // Remove from hash ring
        hashRing.values().removeIf(addr -> addr.equals(address));
    }
    
    /**
     * Gets a server for the given key using consistent hashing.
     * Useful for sticky sessions based on user ID, session ID, etc.
     */
    public String getServerForKey(String key) {
        if (hashRing.isEmpty()) {
            return null;
        }
        
        long hash = hash(key);
        
        // Find the first server clockwise from the hash
        Map.Entry<Long, String> entry = hashRing.ceilingEntry(hash);
        if (entry == null) {
            entry = hashRing.firstEntry();
        }
        
        String server = entry.getValue();
        ServerNode node = serverNodes.get(server);
        
        // If server is unhealthy, find next healthy one
        if (node == null || !node.isHealthy()) {
            server = getNextHealthyServer(hash);
        }
        
        if (server != null) {
            node = serverNodes.get(server);
            if (node != null) {
                node.totalRequests.incrementAndGet();
            }
        }
        
        return server;
    }
    
    private String getNextHealthyServer(long startHash) {
        Long currentHash = startHash;
        int attempts = 0;
        int maxAttempts = hashRing.size();
        
        while (attempts++ < maxAttempts) {
            Map.Entry<Long, String> entry = hashRing.higherEntry(currentHash);
            if (entry == null) {
                entry = hashRing.firstEntry();
            }
            
            String server = entry.getValue();
            ServerNode node = serverNodes.get(server);
            if (node != null && node.isHealthy()) {
                return server;
            }
            
            currentHash = entry.getKey();
        }
        
        return null; // No healthy servers
    }
    
    /**
     * Gets a server using the configured algorithm (not key-based).
     */
    public String getServer() {
        switch (algorithm) {
            case ROUND_ROBIN:
                return getServerRoundRobin();
            case LEAST_CONNECTIONS:
                return getServerLeastConnections();
            case RANDOM:
                return getServerRandom();
            case CONSISTENT_HASH:
            default:
                // For non-key-based, use random key
                return getServerForKey(UUID.randomUUID().toString());
        }
    }
    
    private final AtomicInteger roundRobinIndex = new AtomicInteger(0);
    
    private String getServerRoundRobin() {
        List<String> healthy = getHealthyServers();
        if (healthy.isEmpty()) return null;
        
        int idx = roundRobinIndex.getAndUpdate(i -> (i + 1) % healthy.size());
        return healthy.get(idx % healthy.size());
    }
    
    private String getServerLeastConnections() {
        return getHealthyServers().stream()
            .min(Comparator.comparingInt(addr -> 
                activeConnections.getOrDefault(addr, new AtomicInteger(0)).get()))
            .orElse(null);
    }
    
    private String getServerRandom() {
        List<String> healthy = getHealthyServers();
        if (healthy.isEmpty()) return null;
        return healthy.get(ThreadLocalRandom.current().nextInt(healthy.size()));
    }
    
    /**
     * Marks a connection as started (for least connections tracking).
     */
    public void connectionStarted(String server) {
        AtomicInteger counter = activeConnections.get(server);
        if (counter != null) {
            counter.incrementAndGet();
        }
    }
    
    /**
     * Marks a connection as ended.
     */
    public void connectionEnded(String server) {
        AtomicInteger counter = activeConnections.get(server);
        if (counter != null) {
            counter.decrementAndGet();
        }
    }
    
    /**
     * Reports a successful request.
     */
    public void recordSuccess(String server, long responseTimeMs) {
        ServerNode node = serverNodes.get(server);
        if (node != null) {
            node.recordSuccess(responseTimeMs);
        }
        metrics.recordRequest(server, true);
    }
    
    /**
     * Reports a failed request.
     */
    public void recordFailure(String server) {
        ServerNode node = serverNodes.get(server);
        if (node != null) {
            node.recordFailure();
            if (node.getFailureCount() >= healthConfig.unhealthyThreshold) {
                node.markUnhealthy();
            }
        }
        metrics.recordRequest(server, false);
    }
    
    private void performHealthChecks() {
        for (ServerNode node : serverNodes.values()) {
            boolean healthy = healthConfig.checker.check(
                node.getAddress(), 
                healthConfig.timeoutMs
            );
            
            if (healthy) {
                if (!node.isHealthy()) {
                    node.successCount.incrementAndGet();
                    if (node.successCount.get() >= healthConfig.healthyThreshold) {
                        node.markHealthy();
                    }
                } else {
                    node.failureCount.set(0);
                }
            } else {
                node.recordFailure();
                if (node.isHealthy() && 
                    node.getFailureCount() >= healthConfig.unhealthyThreshold) {
                    node.markUnhealthy();
                }
            }
        }
    }
    
    private List<String> getHealthyServers() {
        List<String> healthy = new ArrayList<>();
        for (ServerNode node : serverNodes.values()) {
            if (node.isHealthy()) {
                healthy.add(node.getAddress());
            }
        }
        return healthy;
    }
    
    /**
     * Computes hash using MD5.
     */
    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
            return ((long)(digest[0] & 0xFF) << 24) |
                   ((long)(digest[1] & 0xFF) << 16) |
                   ((long)(digest[2] & 0xFF) << 8) |
                   ((long)(digest[3] & 0xFF));
        } catch (NoSuchAlgorithmException e) {
            return key.hashCode();
        }
    }
    
    public void setAlgorithm(Algorithm algorithm) {
        this.algorithm = algorithm;
    }
    
    public Metrics getMetrics() {
        return metrics;
    }
    
    public int getServerCount() {
        return serverNodes.size();
    }
    
    public int getHealthyServerCount() {
        return getHealthyServers().size();
    }
    
    public void shutdown() {
        scheduler.shutdown();
    }
}
