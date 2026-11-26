/**
 * V1: Simple Proxy Cache
 * 
 * A basic CDN edge node simulation with TTL-based caching.
 * Demonstrates the fundamental concept of caching content
 * at a proxy layer to reduce origin requests.
 * 
 * Features:
 * - Simple HashMap cache with TTL
 * - Cache hit/miss tracking
 * - Simulated origin fetching
 */

import java.util.HashMap;
import java.util.Map;

public class SimpleProxyCache {
    
    private final Map<String, CacheEntry> cache = new HashMap<>();
    private final OriginServer origin;
    private final long defaultTtlMs;
    
    // Statistics
    private long hits = 0;
    private long misses = 0;
    
    public SimpleProxyCache(OriginServer origin, long defaultTtlMs) {
        this.origin = origin;
        this.defaultTtlMs = defaultTtlMs;
    }
    
    /**
     * Fetches content, serving from cache if available.
     */
    public String fetch(String url) {
        CacheEntry entry = cache.get(url);
        
        if (entry != null && !entry.isExpired()) {
            hits++;
            System.out.println("CACHE HIT: " + url);
            return entry.content;
        }
        
        // Cache miss - fetch from origin
        misses++;
        System.out.println("CACHE MISS: " + url + " - fetching from origin");
        
        String content = origin.fetch(url);
        if (content != null) {
            cache.put(url, new CacheEntry(content, defaultTtlMs));
        }
        
        return content;
    }
    
    /**
     * Invalidates (purges) a URL from cache.
     */
    public void purge(String url) {
        cache.remove(url);
        System.out.println("PURGED: " + url);
    }
    
    /**
     * Invalidates all cached content.
     */
    public void purgeAll() {
        cache.clear();
        System.out.println("PURGED ALL");
    }
    
    public double getHitRate() {
        long total = hits + misses;
        return total > 0 ? (hits * 100.0 / total) : 0.0;
    }
    
    public String getStats() {
        return String.format("Hits: %d, Misses: %d, Hit Rate: %.2f%%", 
                           hits, misses, getHitRate());
    }
    
    /**
     * Cache entry with content and expiration.
     */
    private static class CacheEntry {
        final String content;
        final long expirationTime;
        
        CacheEntry(String content, long ttlMs) {
            this.content = content;
            this.expirationTime = System.currentTimeMillis() + ttlMs;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
    }
    
    /**
     * Simulated origin server.
     */
    public interface OriginServer {
        String fetch(String url);
    }
}
