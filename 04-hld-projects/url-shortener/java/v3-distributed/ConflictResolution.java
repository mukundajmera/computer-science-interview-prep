/**
 * URL Shortener - V3 Distributed
 * 
 * Conflict resolution and data synchronization.
 * Handles eventual consistency across regions.
 */

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Conflict resolution strategy.
 */
enum ConflictResolutionStrategy {
    LAST_WRITE_WINS,      // Most recent timestamp wins
    FIRST_WRITE_WINS,     // Original creation wins
    MERGE                  // Merge metadata
}

/**
 * Versioned URL entity for conflict detection.
 */
class VersionedUrlEntity {
    private final String shortCode;
    private final String longUrl;
    private final Instant createdAt;
    private final Instant updatedAt;
    private final String originRegion;
    private final long version;
    private final VectorClock vectorClock;
    
    public VersionedUrlEntity(String shortCode, String longUrl, 
                              String originRegion, long version) {
        this.shortCode = shortCode;
        this.longUrl = longUrl;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
        this.originRegion = originRegion;
        this.version = version;
        this.vectorClock = new VectorClock();
    }
    
    public VersionedUrlEntity withUpdate(Instant updatedAt, long newVersion) {
        VersionedUrlEntity updated = new VersionedUrlEntity(
            this.shortCode, this.longUrl, this.originRegion, newVersion);
        return updated;
    }
    
    // Getters
    public String getShortCode() { return shortCode; }
    public String getLongUrl() { return longUrl; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public String getOriginRegion() { return originRegion; }
    public long getVersion() { return version; }
    public VectorClock getVectorClock() { return vectorClock; }
}

/**
 * Vector clock for causality tracking.
 */
class VectorClock {
    private final Map<String, Long> clocks;
    
    public VectorClock() {
        this.clocks = new ConcurrentHashMap<>();
    }
    
    public VectorClock(Map<String, Long> clocks) {
        this.clocks = new ConcurrentHashMap<>(clocks);
    }
    
    /**
     * Increment clock for a node.
     */
    public void increment(String nodeId) {
        clocks.merge(nodeId, 1L, Long::sum);
    }
    
    /**
     * Merge with another vector clock.
     */
    public VectorClock merge(VectorClock other) {
        Map<String, Long> merged = new ConcurrentHashMap<>(this.clocks);
        
        for (Map.Entry<String, Long> entry : other.clocks.entrySet()) {
            merged.merge(entry.getKey(), entry.getValue(), Math::max);
        }
        
        return new VectorClock(merged);
    }
    
    /**
     * Check if this clock happened before another.
     */
    public boolean happenedBefore(VectorClock other) {
        boolean atLeastOneLess = false;
        
        for (String nodeId : clocks.keySet()) {
            long thisValue = clocks.getOrDefault(nodeId, 0L);
            long otherValue = other.clocks.getOrDefault(nodeId, 0L);
            
            if (thisValue > otherValue) {
                return false; // This happened after
            }
            if (thisValue < otherValue) {
                atLeastOneLess = true;
            }
        }
        
        // Check for keys only in other
        for (String nodeId : other.clocks.keySet()) {
            if (!clocks.containsKey(nodeId) && other.clocks.get(nodeId) > 0) {
                atLeastOneLess = true;
            }
        }
        
        return atLeastOneLess;
    }
    
    /**
     * Check if clocks are concurrent (neither happened before the other).
     */
    public boolean isConcurrent(VectorClock other) {
        return !this.happenedBefore(other) && !other.happenedBefore(this);
    }
    
    public Map<String, Long> getClocks() {
        return new ConcurrentHashMap<>(clocks);
    }
}

/**
 * Conflict resolver for multi-region consistency.
 */
class ConflictResolver {
    
    private final ConflictResolutionStrategy strategy;
    
    public ConflictResolver(ConflictResolutionStrategy strategy) {
        this.strategy = strategy;
    }
    
    /**
     * Resolve conflict between two versions.
     */
    public VersionedUrlEntity resolve(VersionedUrlEntity local, 
                                       VersionedUrlEntity remote) {
        if (local == null) return remote;
        if (remote == null) return local;
        
        // Check causality using vector clocks
        if (local.getVectorClock().happenedBefore(remote.getVectorClock())) {
            return remote; // Remote is newer
        }
        if (remote.getVectorClock().happenedBefore(local.getVectorClock())) {
            return local; // Local is newer
        }
        
        // Concurrent updates - apply strategy
        switch (strategy) {
            case LAST_WRITE_WINS:
                return local.getUpdatedAt().isAfter(remote.getUpdatedAt()) 
                    ? local : remote;
                    
            case FIRST_WRITE_WINS:
                return local.getCreatedAt().isBefore(remote.getCreatedAt())
                    ? local : remote;
                    
            case MERGE:
                // For URLs, merge doesn't make sense - use last write wins
                return local.getUpdatedAt().isAfter(remote.getUpdatedAt())
                    ? local : remote;
                    
            default:
                return local;
        }
    }
}

/**
 * Sync manager for cross-region data synchronization.
 */
class SyncManager {
    
    private final String localRegion;
    private final Map<String, RegionalService> regionalServices;
    private final ConflictResolver conflictResolver;
    private final Map<String, Long> syncPositions;
    
    public SyncManager(String localRegion,
                      Map<String, RegionalService> regionalServices,
                      ConflictResolver conflictResolver) {
        this.localRegion = localRegion;
        this.regionalServices = regionalServices;
        this.conflictResolver = conflictResolver;
        this.syncPositions = new ConcurrentHashMap<>();
    }
    
    /**
     * Sync with a remote region.
     * @param remoteRegion The region to sync with
     * @return Number of records synced
     */
    public int syncWithRegion(String remoteRegion) {
        RegionalService remoteService = regionalServices.get(remoteRegion);
        RegionalService localService = regionalServices.get(localRegion);
        
        if (remoteService == null || localService == null) {
            return 0;
        }
        
        // In production: Get changes since last sync position
        // and apply with conflict resolution
        
        return 0;
    }
    
    /**
     * Full sync across all regions.
     * @return Total records synced
     */
    public int fullSync() {
        int total = 0;
        
        for (String region : regionalServices.keySet()) {
            if (!region.equals(localRegion)) {
                total += syncWithRegion(region);
            }
        }
        
        return total;
    }
}

/**
 * Anti-entropy service for detecting and repairing inconsistencies.
 */
class AntiEntropyService implements Runnable {
    
    private final SyncManager syncManager;
    private final long intervalMs;
    private volatile boolean running = true;
    
    public AntiEntropyService(SyncManager syncManager, long intervalMs) {
        this.syncManager = syncManager;
        this.intervalMs = intervalMs;
    }
    
    @Override
    public void run() {
        while (running) {
            try {
                int synced = syncManager.fullSync();
                if (synced > 0) {
                    System.out.println("Anti-entropy: synced " + synced + " records");
                }
                
                Thread.sleep(intervalMs);
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                System.err.println("Anti-entropy error: " + e.getMessage());
            }
        }
    }
    
    public void stop() {
        running = false;
    }
}
