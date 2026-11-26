package v2_realistic;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/**
 * V2: Weighted Round Robin Load Balancer with Health Checks
 * 
 * A more realistic load balancer that:
 * - Supports weighted distribution
 * - Performs health checks
 * - Removes unhealthy servers automatically
 * 
 * Features:
 * - Weighted round robin algorithm
 * - Configurable server weights
 * - Background health checking
 * - Thread-safe operations
 */
public class WeightedLoadBalancer {
    
    private final List<Server> servers;
    private final List<Server> healthyServers;
    private final AtomicInteger currentIndex;
    private final ScheduledExecutorService healthChecker;
    private final HealthCheckConfig healthConfig;
    
    // Statistics
    private final Map<String, AtomicLong> requestCounts = new ConcurrentHashMap<>();
    
    /**
     * Server representation with weight and health status.
     */
    public static class Server {
        private final String address;
        private final int weight;
        private volatile boolean healthy = true;
        private volatile int consecutiveFailures = 0;
        private volatile long lastCheckTime = 0;
        
        public Server(String address, int weight) {
            this.address = address;
            this.weight = weight;
        }
        
        public String getAddress() { return address; }
        public int getWeight() { return weight; }
        public boolean isHealthy() { return healthy; }
        
        void markHealthy() {
            this.healthy = true;
            this.consecutiveFailures = 0;
        }
        
        void markUnhealthy() {
            this.healthy = false;
        }
        
        void recordFailure() {
            this.consecutiveFailures++;
        }
        
        int getConsecutiveFailures() {
            return consecutiveFailures;
        }
        
        @Override
        public String toString() {
            return String.format("Server{%s, weight=%d, healthy=%s}", 
                address, weight, healthy);
        }
    }
    
    /**
     * Health check configuration.
     */
    public static class HealthCheckConfig {
        public int intervalSeconds = 5;
        public int timeoutMillis = 2000;
        public int unhealthyThreshold = 3;
        public int healthyThreshold = 2;
        public HealthChecker checker = address -> true; // Default: always healthy
    }
    
    /**
     * Interface for health check implementation.
     */
    @FunctionalInterface
    public interface HealthChecker {
        boolean check(String address);
    }
    
    /**
     * Creates a weighted load balancer.
     */
    public WeightedLoadBalancer(List<Server> servers, HealthCheckConfig config) {
        this.servers = new CopyOnWriteArrayList<>(servers);
        this.healthyServers = new CopyOnWriteArrayList<>();
        this.currentIndex = new AtomicInteger(0);
        this.healthConfig = config;
        
        // Initialize request counts
        for (Server server : servers) {
            requestCounts.put(server.getAddress(), new AtomicLong(0));
        }
        
        // Build initial healthy server list (weighted)
        rebuildHealthyList();
        
        // Start health checker
        this.healthChecker = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "health-checker");
            t.setDaemon(true);
            return t;
        });
        
        healthChecker.scheduleAtFixedRate(
            this::performHealthChecks,
            config.intervalSeconds,
            config.intervalSeconds,
            TimeUnit.SECONDS
        );
    }
    
    /**
     * Gets the next server using weighted round robin.
     * Only returns healthy servers.
     * 
     * @return Server address or null if no healthy servers
     */
    public String getNextServer() {
        if (healthyServers.isEmpty()) {
            return null;
        }
        
        int index = currentIndex.getAndUpdate(i -> 
            (i + 1) % healthyServers.size());
        
        Server server = healthyServers.get(index % healthyServers.size());
        requestCounts.get(server.getAddress()).incrementAndGet();
        
        return server.getAddress();
    }
    
    /**
     * Rebuilds the healthy server list with weights.
     * A server with weight 3 appears 3 times in the list.
     */
    private synchronized void rebuildHealthyList() {
        healthyServers.clear();
        for (Server server : servers) {
            if (server.isHealthy()) {
                for (int i = 0; i < server.getWeight(); i++) {
                    healthyServers.add(server);
                }
            }
        }
    }
    
    /**
     * Performs health checks on all servers.
     */
    private void performHealthChecks() {
        boolean changed = false;
        
        for (Server server : servers) {
            boolean isHealthy = healthConfig.checker.check(server.getAddress());
            
            if (isHealthy) {
                if (!server.isHealthy()) {
                    server.consecutiveFailures = 0;
                    // Need multiple successes to mark healthy
                    if (++server.consecutiveFailures >= healthConfig.healthyThreshold) {
                        server.markHealthy();
                        changed = true;
                        System.out.println("Server became healthy: " + server.getAddress());
                    }
                } else {
                    server.consecutiveFailures = 0;
                }
            } else {
                server.recordFailure();
                if (server.isHealthy() && 
                    server.getConsecutiveFailures() >= healthConfig.unhealthyThreshold) {
                    server.markUnhealthy();
                    changed = true;
                    System.out.println("Server became unhealthy: " + server.getAddress());
                }
            }
            
            server.lastCheckTime = System.currentTimeMillis();
        }
        
        if (changed) {
            rebuildHealthyList();
        }
    }
    
    /**
     * Manually marks a server as unhealthy.
     */
    public void markServerUnhealthy(String address) {
        for (Server server : servers) {
            if (server.getAddress().equals(address)) {
                server.markUnhealthy();
                rebuildHealthyList();
                break;
            }
        }
    }
    
    /**
     * Returns statistics about request distribution.
     */
    public Map<String, Long> getRequestDistribution() {
        Map<String, Long> distribution = new HashMap<>();
        requestCounts.forEach((addr, count) -> 
            distribution.put(addr, count.get()));
        return distribution;
    }
    
    /**
     * Returns all servers with their status.
     */
    public List<Server> getAllServers() {
        return new ArrayList<>(servers);
    }
    
    /**
     * Returns count of healthy servers.
     */
    public int getHealthyServerCount() {
        return (int) servers.stream().filter(Server::isHealthy).count();
    }
    
    /**
     * Shuts down the health checker.
     */
    public void shutdown() {
        healthChecker.shutdown();
    }
}
