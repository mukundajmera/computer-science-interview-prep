/**
 * V3: Production CDN with Cache Invalidation
 * 
 * Production-grade CDN simulator with versioning, purge API,
 * stale-while-revalidate, and comprehensive metrics.
 * 
 * Features:
 * - Versioned URL support
 * - Purge API with global propagation
 * - Stale-while-revalidate
 * - Cache-Control header parsing
 * - Metrics and monitoring
 * - Thread-safe operations
 */

import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public class ProductionCDN {
    
    private final Map<String, EdgeNode> edges = new ConcurrentHashMap<>();
    private final OriginServer origin;
    private final EdgeNode shield;
    private final ExecutorService revalidationExecutor;
    private final CdnMetrics metrics = new CdnMetrics();
    
    public ProductionCDN(OriginServer origin) {
        this.origin = origin;
        this.revalidationExecutor = Executors.newCachedThreadPool();
        this.shield = new EdgeNode("shield", null, origin, metrics, revalidationExecutor);
        
        // Initialize edge nodes
        String[] regions = {"us-east", "us-west", "eu-west", "eu-central", "asia-east", "asia-south"};
        for (String region : regions) {
            edges.put(region, new EdgeNode(region, shield, null, metrics, revalidationExecutor));
        }
    }
    
    /**
     * Fetches content with full CDN behavior.
     */
    public CdnResponse fetch(String userRegion, String url, Map<String, String> headers) {
        EdgeNode edge = routeToEdge(userRegion);
        long startTime = System.nanoTime();
        
        CacheControl cacheControl = CacheControl.parse(headers.get("Cache-Control"));
        
        CacheEntry entry = edge.fetch(url, cacheControl);
        
        long latencyNs = System.nanoTime() - startTime;
        double latencyMs = latencyNs / 1_000_000.0;
        
        metrics.recordLatency(latencyMs);
        
        return new CdnResponse(
            entry.content,
            edge.name,
            entry.source,
            latencyMs,
            entry.wasCacheHit
        );
    }
    
    /**
     * Purges content globally across all edges.
     */
    public CompletableFuture<PurgeResult> purge(String urlPattern) {
        long startTime = System.currentTimeMillis();
        
        CompletableFuture<Void> shieldPurge = CompletableFuture.runAsync(() -> 
            shield.purge(urlPattern));
        
        CompletableFuture<?>[] edgePurges = edges.values().stream()
            .map(edge -> CompletableFuture.runAsync(() -> edge.purge(urlPattern)))
            .toArray(CompletableFuture[]::new);
        
        return CompletableFuture.allOf(shieldPurge)
            .thenCompose(v -> CompletableFuture.allOf(edgePurges))
            .thenApply(v -> {
                long duration = System.currentTimeMillis() - startTime;
                metrics.recordPurge();
                return new PurgeResult(urlPattern, edges.size() + 1, duration);
            });
    }
    
    /**
     * Pre-warms cache by fetching content to all edges.
     */
    public CompletableFuture<Void> warmCache(String url) {
        CompletableFuture<?>[] futures = edges.values().stream()
            .map(edge -> CompletableFuture.runAsync(() -> 
                edge.fetch(url, CacheControl.DEFAULT)))
            .toArray(CompletableFuture[]::new);
        
        return CompletableFuture.allOf(futures);
    }
    
    public CdnMetrics getMetrics() {
        return metrics;
    }
    
    public void shutdown() {
        revalidationExecutor.shutdown();
    }
    
    private EdgeNode routeToEdge(String userRegion) {
        if (userRegion.contains("asia") || userRegion.contains("japan") || 
            userRegion.contains("korea")) {
            return edges.getOrDefault("asia-east", edges.get("us-east"));
        } else if (userRegion.contains("india") || userRegion.contains("australia")) {
            return edges.getOrDefault("asia-south", edges.get("us-west"));
        } else if (userRegion.contains("europe") || userRegion.contains("uk") || 
                   userRegion.contains("germany")) {
            return edges.getOrDefault("eu-west", edges.get("us-east"));
        } else if (userRegion.contains("west") || userRegion.contains("california")) {
            return edges.getOrDefault("us-west", edges.get("us-east"));
        }
        return edges.get("us-east");
    }
    
    // ==================== Inner Classes ====================
    
    /**
     * Cache control directives.
     */
    public static class CacheControl {
        public static final CacheControl DEFAULT = new CacheControl(3600, 0, false, false);
        
        public final int maxAgeSeconds;
        public final int staleWhileRevalidateSeconds;
        public final boolean noCache;
        public final boolean noStore;
        
        public CacheControl(int maxAge, int swr, boolean noCache, boolean noStore) {
            this.maxAgeSeconds = maxAge;
            this.staleWhileRevalidateSeconds = swr;
            this.noCache = noCache;
            this.noStore = noStore;
        }
        
        public static CacheControl parse(String header) {
            if (header == null) return DEFAULT;
            
            int maxAge = 3600;
            int swr = 0;
            boolean noCache = header.contains("no-cache");
            boolean noStore = header.contains("no-store");
            
            if (header.contains("max-age=")) {
                String value = header.split("max-age=")[1].split(",")[0].trim();
                maxAge = Integer.parseInt(value);
            }
            if (header.contains("stale-while-revalidate=")) {
                String value = header.split("stale-while-revalidate=")[1].split(",")[0].trim();
                swr = Integer.parseInt(value);
            }
            
            return new CacheControl(maxAge, swr, noCache, noStore);
        }
    }
    
    /**
     * Cache entry with TTL and stale-while-revalidate support.
     */
    public static class CacheEntry {
        public final String content;
        public final String source;
        public final boolean wasCacheHit;
        final long expirationTime;
        final long staleUntilTime;
        
        CacheEntry(String content, String source, boolean cacheHit, 
                   long ttlMs, long swrMs) {
            this.content = content;
            this.source = source;
            this.wasCacheHit = cacheHit;
            this.expirationTime = System.currentTimeMillis() + ttlMs;
            this.staleUntilTime = this.expirationTime + swrMs;
        }
        
        boolean isFresh() {
            return System.currentTimeMillis() < expirationTime;
        }
        
        boolean isStale() {
            long now = System.currentTimeMillis();
            return now >= expirationTime && now < staleUntilTime;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() >= staleUntilTime;
        }
    }
    
    /**
     * Edge node with production caching features.
     */
    public static class EdgeNode {
        final String name;
        private final EdgeNode parent;
        private final OriginServer origin;
        private final CdnMetrics metrics;
        private final ExecutorService revalidationExecutor;
        private final ConcurrentMap<String, CacheEntry> cache = new ConcurrentHashMap<>();
        private final ConcurrentMap<String, Boolean> revalidatingKeys = new ConcurrentHashMap<>();
        
        EdgeNode(String name, EdgeNode parent, OriginServer origin, 
                 CdnMetrics metrics, ExecutorService executor) {
            this.name = name;
            this.parent = parent;
            this.origin = origin;
            this.metrics = metrics;
            this.revalidationExecutor = executor;
        }
        
        public CacheEntry fetch(String url, CacheControl cc) {
            if (cc.noStore) {
                return fetchFromUpstream(url, cc);
            }
            
            CacheEntry entry = cache.get(url);
            
            if (entry != null && entry.isFresh() && !cc.noCache) {
                if (parent != null) {
                    metrics.recordHit();
                }
                return new CacheEntry(entry.content, name + " (hit)", true,
                    entry.expirationTime - System.currentTimeMillis(), 0);
            }
            
            if (entry != null && entry.isStale() && !cc.noCache) {
                // Stale-while-revalidate: return stale, refresh in background
                triggerRevalidation(url, cc);
                if (parent != null) {
                    metrics.recordHit();
                }
                return new CacheEntry(entry.content, name + " (stale)", true, 0, 0);
            }
            
            if (parent != null) {
                metrics.recordMiss();
            }
            return fetchFromUpstream(url, cc);
        }
        
        private CacheEntry fetchFromUpstream(String url, CacheControl cc) {
            String content;
            String source;
            
            if (parent != null) {
                CacheEntry parentEntry = parent.fetch(url, cc);
                content = parentEntry.content;
                source = parentEntry.source;
            } else if (origin != null) {
                content = origin.fetch(url);
                source = "origin";
            } else {
                return null;
            }
            
            if (!cc.noStore && content != null) {
                long ttlMs = cc.maxAgeSeconds * 1000L;
                long swrMs = cc.staleWhileRevalidateSeconds * 1000L;
                CacheEntry newEntry = new CacheEntry(content, source, false, ttlMs, swrMs);
                cache.put(url, newEntry);
            }
            
            return new CacheEntry(content, source, false, 0, 0);
        }
        
        private void triggerRevalidation(String url, CacheControl cc) {
            if (revalidatingKeys.putIfAbsent(url, true) == null) {
                revalidationExecutor.submit(() -> {
                    try {
                        fetchFromUpstream(url, cc);
                    } finally {
                        revalidatingKeys.remove(url);
                    }
                });
            }
        }
        
        public void purge(String urlPattern) {
            if (urlPattern.endsWith("*")) {
                String prefix = urlPattern.substring(0, urlPattern.length() - 1);
                cache.keySet().removeIf(key -> key.startsWith(prefix));
            } else {
                cache.remove(urlPattern);
            }
        }
    }
    
    /**
     * CDN-wide metrics.
     */
    public static class CdnMetrics {
        private final AtomicLong hits = new AtomicLong();
        private final AtomicLong misses = new AtomicLong();
        private final AtomicLong purges = new AtomicLong();
        private final AtomicLong totalLatencyMicros = new AtomicLong();
        private final AtomicLong requestCount = new AtomicLong();
        
        void recordHit() { hits.incrementAndGet(); }
        void recordMiss() { misses.incrementAndGet(); }
        void recordPurge() { purges.incrementAndGet(); }
        void recordLatency(double ms) {
            totalLatencyMicros.addAndGet((long)(ms * 1000));
            requestCount.incrementAndGet();
        }
        
        public double getHitRate() {
            long total = hits.get() + misses.get();
            return total > 0 ? (hits.get() * 100.0 / total) : 0;
        }
        
        public double getAverageLatencyMs() {
            long count = requestCount.get();
            return count > 0 ? (totalLatencyMicros.get() / count / 1000.0) : 0;
        }
        
        @Override
        public String toString() {
            return String.format(
                "CDN Metrics: Hits=%d, Misses=%d, HitRate=%.2f%%, AvgLatency=%.2fms, Purges=%d",
                hits.get(), misses.get(), getHitRate(), getAverageLatencyMs(), purges.get());
        }
    }
    
    /**
     * Response from CDN.
     */
    public static class CdnResponse {
        public final String content;
        public final String servedByEdge;
        public final String source;
        public final double latencyMs;
        public final boolean cacheHit;
        
        CdnResponse(String content, String edge, String source, double latencyMs, boolean hit) {
            this.content = content;
            this.servedByEdge = edge;
            this.source = source;
            this.latencyMs = latencyMs;
            this.cacheHit = hit;
        }
        
        @Override
        public String toString() {
            return String.format("Edge: %s, Source: %s, Latency: %.2fms, CacheHit: %s",
                servedByEdge, source, latencyMs, cacheHit);
        }
    }
    
    /**
     * Purge operation result.
     */
    public static class PurgeResult {
        public final String pattern;
        public final int nodesAffected;
        public final long durationMs;
        
        PurgeResult(String pattern, int nodes, long duration) {
            this.pattern = pattern;
            this.nodesAffected = nodes;
            this.durationMs = duration;
        }
        
        @Override
        public String toString() {
            return String.format("Purged '%s' from %d nodes in %dms", 
                pattern, nodesAffected, durationMs);
        }
    }
    
    /**
     * Origin server interface.
     */
    public interface OriginServer {
        String fetch(String url);
    }
}
