/**
 * URL Shortener - V3 Distributed
 * 
 * Multi-region distributed URL shortening service.
 * Handles global traffic with regional routing and replication.
 */

import java.time.Instant;
import java.util.Optional;
import java.util.List;
import java.util.Map;

/**
 * Region-aware URL service for multi-region deployment.
 */
interface DistributedUrlService extends UrlShorteningService {
    /**
     * Get the current region.
     * @return Region identifier
     */
    String getCurrentRegion();
    
    /**
     * Route request to optimal region.
     * @param shortCode The short code
     * @return Region where data lives
     */
    String getDataRegion(String shortCode);
    
    /**
     * Replicate URL to other regions.
     * @param shortCode The short code
     * @param targetRegions Target regions
     */
    void replicateToRegions(String shortCode, List<String> targetRegions);
}

/**
 * Circuit breaker for fault tolerance.
 */
interface CircuitBreaker {
    /**
     * Check if circuit is open (blocking requests).
     * @return true if open
     */
    boolean isOpen();
    
    /**
     * Record a success.
     */
    void recordSuccess();
    
    /**
     * Record a failure.
     */
    void recordFailure();
    
    /**
     * Execute with circuit breaker protection.
     * @param operation The operation to execute
     * @param fallback Fallback if circuit is open
     * @return Result of operation or fallback
     */
    <T> T execute(java.util.function.Supplier<T> operation, 
                  java.util.function.Supplier<T> fallback);
}

/**
 * Distributed cache interface for multi-region caching.
 */
interface DistributedCache extends UrlCache {
    /**
     * Get from local cache only.
     * @param shortCode The short code
     * @return Cached value if present locally
     */
    Optional<String> getLocal(String shortCode);
    
    /**
     * Invalidate across all regions.
     * @param shortCode The short code
     */
    void invalidateGlobal(String shortCode);
    
    /**
     * Get cache statistics.
     * @return Cache stats
     */
    CacheStats getStats();
}

/**
 * Cache statistics.
 */
class CacheStats {
    private final long hits;
    private final long misses;
    private final long evictions;
    private final double hitRatio;
    
    public CacheStats(long hits, long misses, long evictions) {
        this.hits = hits;
        this.misses = misses;
        this.evictions = evictions;
        this.hitRatio = (hits + misses) > 0 ? 
            (double) hits / (hits + misses) : 0.0;
    }
    
    public long getHits() { return hits; }
    public long getMisses() { return misses; }
    public long getEvictions() { return evictions; }
    public double getHitRatio() { return hitRatio; }
}

/**
 * Multi-region URL shortening service.
 * Handles cross-region replication and conflict resolution.
 */
class MultiRegionUrlService implements DistributedUrlService {
    
    private final String currentRegion;
    private final Map<String, RegionalService> regionalServices;
    private final ConsistentHashRouter router;
    private final DistributedCache cache;
    private final ReplicationManager replicationManager;
    private final CircuitBreaker circuitBreaker;
    private final String baseUrl;
    
    public MultiRegionUrlService(String currentRegion,
                                 Map<String, RegionalService> regionalServices,
                                 DistributedCache cache,
                                 String baseUrl) {
        this.currentRegion = currentRegion;
        this.regionalServices = regionalServices;
        this.router = new ConsistentHashRouter(regionalServices.keySet());
        this.cache = cache;
        this.replicationManager = new ReplicationManager(regionalServices);
        this.circuitBreaker = new SimpleCircuitBreaker(5, 30000);
        this.baseUrl = baseUrl;
    }
    
    @Override
    public CreateUrlResponse createShortUrl(CreateUrlRequest request) {
        // Create locally first
        RegionalService localService = regionalServices.get(currentRegion);
        CreateUrlResponse response = localService.createUrl(request, baseUrl);
        
        // Async replication to other regions
        List<String> otherRegions = regionalServices.keySet().stream()
            .filter(r -> !r.equals(currentRegion))
            .collect(java.util.stream.Collectors.toList());
        
        replicationManager.replicateAsync(response.getShortCode(), 
                                          request.getLongUrl(), 
                                          otherRegions);
        
        // Populate cache
        cache.put(response.getShortCode(), request.getLongUrl(), 86400);
        
        return response;
    }
    
    @Override
    public Optional<String> getOriginalUrl(String shortCode) {
        // Try local cache first
        Optional<String> cached = cache.getLocal(shortCode);
        if (cached.isPresent()) {
            return cached;
        }
        
        // Try distributed cache
        cached = cache.get(shortCode);
        if (cached.isPresent()) {
            return cached;
        }
        
        // Determine data region
        String dataRegion = getDataRegion(shortCode);
        RegionalService service = regionalServices.get(dataRegion);
        
        // Execute with circuit breaker
        return circuitBreaker.execute(
            () -> {
                Optional<String> url = service.getUrl(shortCode);
                url.ifPresent(u -> cache.put(shortCode, u, 86400));
                return url;
            },
            () -> {
                // Fallback: try other regions
                for (String region : regionalServices.keySet()) {
                    if (!region.equals(dataRegion)) {
                        Optional<String> url = regionalServices.get(region).getUrl(shortCode);
                        if (url.isPresent()) {
                            return url;
                        }
                    }
                }
                return Optional.empty();
            }
        );
    }
    
    @Override
    public Optional<UrlStats> getStats(String shortCode) {
        String dataRegion = getDataRegion(shortCode);
        return regionalServices.get(dataRegion).getStats(shortCode);
    }
    
    @Override
    public boolean deleteUrl(String shortCode) {
        // Delete from all regions
        boolean deleted = false;
        for (RegionalService service : regionalServices.values()) {
            if (service.deleteUrl(shortCode)) {
                deleted = true;
            }
        }
        
        // Invalidate cache globally
        cache.invalidateGlobal(shortCode);
        
        return deleted;
    }
    
    @Override
    public String getCurrentRegion() {
        return currentRegion;
    }
    
    @Override
    public String getDataRegion(String shortCode) {
        return router.getRegion(shortCode);
    }
    
    @Override
    public void replicateToRegions(String shortCode, List<String> targetRegions) {
        RegionalService localService = regionalServices.get(currentRegion);
        Optional<String> url = localService.getUrl(shortCode);
        
        if (url.isPresent()) {
            for (String region : targetRegions) {
                if (!region.equals(currentRegion)) {
                    regionalServices.get(region).replicate(shortCode, url.get());
                }
            }
        }
    }
}

/**
 * Regional service interface for region-specific operations.
 */
interface RegionalService {
    CreateUrlResponse createUrl(CreateUrlRequest request, String baseUrl);
    Optional<String> getUrl(String shortCode);
    Optional<UrlStats> getStats(String shortCode);
    boolean deleteUrl(String shortCode);
    void replicate(String shortCode, String longUrl);
    String getRegion();
}

/**
 * Consistent hash router for data placement.
 */
class ConsistentHashRouter {
    
    private final java.util.TreeMap<Integer, String> ring;
    private final int virtualNodes;
    
    public ConsistentHashRouter(java.util.Set<String> regions) {
        this.ring = new java.util.TreeMap<>();
        this.virtualNodes = 100;
        
        for (String region : regions) {
            addRegion(region);
        }
    }
    
    private void addRegion(String region) {
        for (int i = 0; i < virtualNodes; i++) {
            int hash = hash(region + "-" + i);
            ring.put(hash, region);
        }
    }
    
    public String getRegion(String key) {
        if (ring.isEmpty()) {
            throw new IllegalStateException("No regions available");
        }
        
        int hash = hash(key);
        Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
        
        if (entry == null) {
            entry = ring.firstEntry();
        }
        
        return entry.getValue();
    }
    
    private int hash(String key) {
        // Simple hash function (use MD5/MurmurHash in production)
        return key.hashCode() & 0x7FFFFFFF;
    }
}

/**
 * Replication manager for async cross-region replication.
 */
class ReplicationManager {
    
    private final Map<String, RegionalService> regionalServices;
    private final java.util.concurrent.ExecutorService executor;
    
    public ReplicationManager(Map<String, RegionalService> regionalServices) {
        this.regionalServices = regionalServices;
        this.executor = java.util.concurrent.Executors.newFixedThreadPool(4);
    }
    
    public void replicateAsync(String shortCode, String longUrl, List<String> targetRegions) {
        for (String region : targetRegions) {
            executor.submit(() -> {
                try {
                    RegionalService service = regionalServices.get(region);
                    if (service != null) {
                        service.replicate(shortCode, longUrl);
                    }
                } catch (Exception e) {
                    System.err.println("Replication failed to " + region + ": " + e.getMessage());
                    // In production: Retry with exponential backoff
                }
            });
        }
    }
    
    public void shutdown() {
        executor.shutdown();
    }
}

/**
 * Simple circuit breaker implementation.
 */
class SimpleCircuitBreaker implements CircuitBreaker {
    
    private final int failureThreshold;
    private final long resetTimeMs;
    
    private int failureCount = 0;
    private long lastFailureTime = 0;
    private boolean open = false;
    
    public SimpleCircuitBreaker(int failureThreshold, long resetTimeMs) {
        this.failureThreshold = failureThreshold;
        this.resetTimeMs = resetTimeMs;
    }
    
    @Override
    public synchronized boolean isOpen() {
        if (open && System.currentTimeMillis() - lastFailureTime > resetTimeMs) {
            // Half-open state - allow one request
            open = false;
            failureCount = 0;
        }
        return open;
    }
    
    @Override
    public synchronized void recordSuccess() {
        failureCount = 0;
        open = false;
    }
    
    @Override
    public synchronized void recordFailure() {
        failureCount++;
        lastFailureTime = System.currentTimeMillis();
        
        if (failureCount >= failureThreshold) {
            open = true;
        }
    }
    
    @Override
    public <T> T execute(java.util.function.Supplier<T> operation, 
                         java.util.function.Supplier<T> fallback) {
        if (isOpen()) {
            return fallback.get();
        }
        
        try {
            T result = operation.get();
            recordSuccess();
            return result;
        } catch (Exception e) {
            recordFailure();
            return fallback.get();
        }
    }
}

// ============================================================================
// Pattern Integration Hooks (Real-time transport, contention, workflow durability)
// ============================================================================

enum DeliveryMode {
    POLLING,
    LONG_POLLING,
    SSE,
    WEBSOCKET
    // WebRTC could be used for peer handoff of QR previews if needed.
}

enum ContentionPolicy {
    OPTIMISTIC,
    PESSIMISTIC,
    SERIAL_QUEUE,
    DISTRIBUTED_LOCK
}

class ExecutionResult {
    private final boolean success;
    private final String checkpointId;
    private final String errorMessage;
    private final boolean retryable;

    private ExecutionResult(boolean success, String checkpointId, String errorMessage, boolean retryable) {
        this.success = success;
        this.checkpointId = checkpointId;
        this.errorMessage = errorMessage;
        this.retryable = retryable;
    }

    public static ExecutionResult success(String checkpointId) {
        return new ExecutionResult(true, checkpointId, null, false);
    }

    public static ExecutionResult failure(String checkpointId, String errorMessage, boolean retryable) {
        return new ExecutionResult(false, checkpointId, errorMessage, retryable);
    }

    public boolean isSuccess() { return success; }
    public String getCheckpointId() { return checkpointId; }
    public String getErrorMessage() { return errorMessage; }
    public boolean isRetryable() { return retryable; }
}

interface WorkflowStep {
    String name();
    ExecutionResult execute();
}

interface CompensationStep {
    String name();
    void compensate(String checkpointId);
}

interface WorkflowOrchestrator {
    ExecutionResult runStep(WorkflowStep step, String idempotencyKey, IdempotencyStore store);
    void registerCompensation(String checkpointId, CompensationStep compensationStep);
}

interface IdempotencyStore {
    boolean hasProcessed(String key);
    void markProcessed(String key, ExecutionResult result);
    Optional<ExecutionResult> getResult(String key);
}
