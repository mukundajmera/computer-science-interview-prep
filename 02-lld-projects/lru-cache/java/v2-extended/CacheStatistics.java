package v2_extended;

/**
 * LRU Cache - V2 Extended
 * 
 * Cache statistics tracking hits, misses, and evictions.
 */
public class CacheStatistics {
    private long hits;
    private long misses;
    private long evictions;
    private long expirations;
    private long puts;
    private long removes;

    public CacheStatistics() {
        reset();
    }

    public void recordHit() {
        hits++;
    }

    public void recordMiss() {
        misses++;
    }

    public void recordEviction() {
        evictions++;
    }

    public void recordExpiration() {
        expirations++;
    }

    public void recordPut() {
        puts++;
    }

    public void recordRemove() {
        removes++;
    }

    public long getHits() {
        return hits;
    }

    public long getMisses() {
        return misses;
    }

    public long getEvictions() {
        return evictions;
    }

    public long getExpirations() {
        return expirations;
    }

    public long getPuts() {
        return puts;
    }

    public long getRemoves() {
        return removes;
    }

    public long getTotalRequests() {
        return hits + misses;
    }

    /**
     * Get cache hit ratio (0.0 to 1.0).
     */
    public double getHitRatio() {
        long total = getTotalRequests();
        return total > 0 ? (double) hits / total : 0.0;
    }

    /**
     * Get cache miss ratio (0.0 to 1.0).
     */
    public double getMissRatio() {
        return 1.0 - getHitRatio();
    }

    /**
     * Reset all statistics.
     */
    public void reset() {
        hits = 0;
        misses = 0;
        evictions = 0;
        expirations = 0;
        puts = 0;
        removes = 0;
    }

    @Override
    public String toString() {
        return String.format(
            "CacheStatistics{hits=%d, misses=%d, hitRatio=%.2f%%, evictions=%d, expirations=%d, puts=%d, removes=%d}",
            hits, misses, getHitRatio() * 100, evictions, expirations, puts, removes
        );
    }
}
