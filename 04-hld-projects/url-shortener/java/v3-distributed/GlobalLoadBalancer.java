/**
 * URL Shortener - V3 Distributed
 * 
 * Global load balancer and request routing.
 * Handles geographic routing and health checking.
 */

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Global load balancer interface.
 */
interface GlobalLoadBalancer {
    /**
     * Get the best region for a request.
     * @param clientLocation Client's geographic location
     * @return Best region for handling the request
     */
    String getBestRegion(String clientLocation);
    
    /**
     * Get healthy regions.
     * @return Set of healthy region identifiers
     */
    Set<String> getHealthyRegions();
    
    /**
     * Mark a region as unhealthy.
     * @param region The region to mark
     */
    void markUnhealthy(String region);
    
    /**
     * Mark a region as healthy.
     * @param region The region to mark
     */
    void markHealthy(String region);
}

/**
 * Region status.
 */
enum RegionStatus {
    HEALTHY,
    DEGRADED,
    UNHEALTHY
}

/**
 * Region health information.
 */
class RegionHealth {
    private final String region;
    private RegionStatus status;
    private long lastHealthCheck;
    private int consecutiveFailures;
    private double latencyMs;
    
    public RegionHealth(String region) {
        this.region = region;
        this.status = RegionStatus.HEALTHY;
        this.lastHealthCheck = System.currentTimeMillis();
        this.consecutiveFailures = 0;
        this.latencyMs = 0;
    }
    
    public void recordSuccess(double latency) {
        this.status = RegionStatus.HEALTHY;
        this.lastHealthCheck = System.currentTimeMillis();
        this.consecutiveFailures = 0;
        this.latencyMs = latency;
    }
    
    public void recordFailure() {
        this.consecutiveFailures++;
        this.lastHealthCheck = System.currentTimeMillis();
        
        if (consecutiveFailures >= 3) {
            this.status = RegionStatus.UNHEALTHY;
        } else if (consecutiveFailures >= 1) {
            this.status = RegionStatus.DEGRADED;
        }
    }
    
    // Getters
    public String getRegion() { return region; }
    public RegionStatus getStatus() { return status; }
    public long getLastHealthCheck() { return lastHealthCheck; }
    public double getLatencyMs() { return latencyMs; }
    public boolean isHealthy() { return status == RegionStatus.HEALTHY; }
}

/**
 * Geographic load balancer implementation.
 * Routes requests to nearest healthy region.
 */
class GeographicLoadBalancer implements GlobalLoadBalancer {
    
    // Client location -> preferred regions (ordered by proximity)
    private final Map<String, List<String>> locationPreferences;
    private final Map<String, RegionHealth> regionHealth;
    
    public GeographicLoadBalancer(Map<String, List<String>> locationPreferences,
                                  Set<String> regions) {
        this.locationPreferences = new ConcurrentHashMap<>(locationPreferences);
        this.regionHealth = new ConcurrentHashMap<>();
        
        for (String region : regions) {
            this.regionHealth.put(region, new RegionHealth(region));
        }
    }
    
    @Override
    public String getBestRegion(String clientLocation) {
        // Get preferred regions for client location
        List<String> preferences = locationPreferences.getOrDefault(
            clientLocation, List.of());
        
        // Find first healthy region in preference order
        for (String region : preferences) {
            RegionHealth health = regionHealth.get(region);
            if (health != null && health.isHealthy()) {
                return region;
            }
        }
        
        // Fallback: any healthy region
        for (RegionHealth health : regionHealth.values()) {
            if (health.isHealthy()) {
                return health.getRegion();
            }
        }
        
        // All unhealthy - return first preference anyway
        if (!preferences.isEmpty()) {
            return preferences.get(0);
        }
        
        // Last resort - return any region
        return regionHealth.keySet().iterator().next();
    }
    
    @Override
    public Set<String> getHealthyRegions() {
        Set<String> healthy = ConcurrentHashMap.newKeySet();
        
        for (RegionHealth health : regionHealth.values()) {
            if (health.isHealthy()) {
                healthy.add(health.getRegion());
            }
        }
        
        return healthy;
    }
    
    @Override
    public void markUnhealthy(String region) {
        RegionHealth health = regionHealth.get(region);
        if (health != null) {
            health.recordFailure();
        }
    }
    
    @Override
    public void markHealthy(String region) {
        RegionHealth health = regionHealth.get(region);
        if (health != null) {
            health.recordSuccess(0);
        }
    }
    
    /**
     * Update health based on latency measurement.
     */
    public void updateHealth(String region, double latencyMs, boolean success) {
        RegionHealth health = regionHealth.get(region);
        if (health != null) {
            if (success) {
                health.recordSuccess(latencyMs);
            } else {
                health.recordFailure();
            }
        }
    }
    
    /**
     * Get region health map for monitoring.
     */
    public Map<String, RegionHealth> getRegionHealth() {
        return new java.util.HashMap<>(regionHealth);
    }
}

/**
 * Health check service for monitoring regions.
 */
class HealthCheckService implements Runnable {
    
    private final GeographicLoadBalancer loadBalancer;
    private final Map<String, String> healthEndpoints;
    private final long checkIntervalMs;
    private volatile boolean running = true;
    
    public HealthCheckService(GeographicLoadBalancer loadBalancer,
                              Map<String, String> healthEndpoints,
                              long checkIntervalMs) {
        this.loadBalancer = loadBalancer;
        this.healthEndpoints = healthEndpoints;
        this.checkIntervalMs = checkIntervalMs;
    }
    
    @Override
    public void run() {
        while (running) {
            for (Map.Entry<String, String> entry : healthEndpoints.entrySet()) {
                String region = entry.getKey();
                String endpoint = entry.getValue();
                
                try {
                    long start = System.currentTimeMillis();
                    boolean healthy = checkHealth(endpoint);
                    long latency = System.currentTimeMillis() - start;
                    
                    loadBalancer.updateHealth(region, latency, healthy);
                    
                } catch (Exception e) {
                    loadBalancer.markUnhealthy(region);
                }
            }
            
            try {
                Thread.sleep(checkIntervalMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    /**
     * Check health of an endpoint.
     * In production: Make HTTP request to health endpoint.
     */
    private boolean checkHealth(String endpoint) {
        // Simulated health check
        // In production: Use HTTP client to check endpoint
        return true;
    }
    
    public void stop() {
        running = false;
    }
}

/**
 * Request router for distributing requests.
 */
class RequestRouter {
    
    private final GlobalLoadBalancer loadBalancer;
    private final Map<String, RegionalService> regionalServices;
    
    public RequestRouter(GlobalLoadBalancer loadBalancer,
                        Map<String, RegionalService> regionalServices) {
        this.loadBalancer = loadBalancer;
        this.regionalServices = regionalServices;
    }
    
    /**
     * Route a request to the appropriate region.
     * @param clientLocation Client's location
     * @return The regional service to handle the request
     */
    public RegionalService route(String clientLocation) {
        String region = loadBalancer.getBestRegion(clientLocation);
        return regionalServices.get(region);
    }
    
    /**
     * Get all healthy services for broadcast operations.
     * @return List of healthy regional services
     */
    public List<RegionalService> getAllHealthy() {
        List<RegionalService> services = new java.util.ArrayList<>();
        
        for (String region : loadBalancer.getHealthyRegions()) {
            RegionalService service = regionalServices.get(region);
            if (service != null) {
                services.add(service);
            }
        }
        
        return services;
    }
}
