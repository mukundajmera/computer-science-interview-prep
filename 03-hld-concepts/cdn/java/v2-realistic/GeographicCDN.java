/**
 * V2: Geographic CDN Simulator
 * 
 * Simulates a CDN with multiple edge locations and geographic routing.
 * Demonstrates how users are routed to nearest edge and how
 * content propagates through the CDN.
 * 
 * Features:
 * - Multiple edge nodes by region
 * - Geographic routing simulation
 * - Origin shield tier
 * - Latency simulation
 */

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class GeographicCDN {
    
    private final Map<String, EdgeNode> edges = new HashMap<>();
    private final OriginServer origin;
    private final EdgeNode shield; // Origin shield
    
    public GeographicCDN(OriginServer origin, long shieldTtlMs, long edgeTtlMs) {
        this.origin = origin;
        this.shield = new EdgeNode("shield", null, origin, shieldTtlMs, 50);
        
        // Create edge nodes in different regions
        edges.put("us-east", new EdgeNode("us-east", shield, null, edgeTtlMs, 10));
        edges.put("us-west", new EdgeNode("us-west", shield, null, edgeTtlMs, 10));
        edges.put("eu-west", new EdgeNode("eu-west", shield, null, edgeTtlMs, 10));
        edges.put("asia-east", new EdgeNode("asia-east", shield, null, edgeTtlMs, 10));
    }
    
    /**
     * Routes user to nearest edge based on their region.
     */
    public EdgeNode routeToEdge(String userRegion) {
        // Simple region mapping
        String edgeRegion = mapUserToEdge(userRegion);
        EdgeNode edge = edges.get(edgeRegion);
        if (edge == null) {
            edge = edges.get("us-east"); // Default
        }
        return edge;
    }
    
    private String mapUserToEdge(String userRegion) {
        if (userRegion.contains("asia") || userRegion.contains("japan") || 
            userRegion.contains("korea") || userRegion.contains("china")) {
            return "asia-east";
        } else if (userRegion.contains("europe") || userRegion.contains("uk") || 
                   userRegion.contains("germany")) {
            return "eu-west";
        } else if (userRegion.contains("california") || userRegion.contains("oregon") ||
                   userRegion.contains("washington")) {
            return "us-west";
        }
        return "us-east";
    }
    
    /**
     * Fetches content for a user from their nearest edge.
     */
    public FetchResult fetch(String userRegion, String url) {
        EdgeNode edge = routeToEdge(userRegion);
        long startTime = System.currentTimeMillis();
        
        String content = edge.fetch(url);
        
        long latency = System.currentTimeMillis() - startTime;
        return new FetchResult(content, edge.name, latency, edge.getLastFetchSource());
    }
    
    /**
     * Purges content from all edges and shield.
     */
    public void purgeGlobal(String url) {
        shield.purge(url);
        for (EdgeNode edge : edges.values()) {
            edge.purge(url);
        }
        System.out.println("Global purge: " + url);
    }
    
    public void printStats() {
        System.out.println("\n=== CDN Statistics ===");
        System.out.println("Shield: " + shield.getStats());
        for (Map.Entry<String, EdgeNode> entry : edges.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue().getStats());
        }
    }
    
    /**
     * Result of a fetch operation.
     */
    public static class FetchResult {
        public final String content;
        public final String servedBy;
        public final long latencyMs;
        public final String source;
        
        FetchResult(String content, String servedBy, long latencyMs, String source) {
            this.content = content;
            this.servedBy = servedBy;
            this.latencyMs = latencyMs;
            this.source = source;
        }
        
        @Override
        public String toString() {
            return String.format("Served by: %s, Source: %s, Latency: %dms", 
                               servedBy, source, latencyMs);
        }
    }
    
    /**
     * Edge node with caching capability.
     */
    public static class EdgeNode {
        final String name;
        private final EdgeNode parent;
        private final OriginServer origin;
        private final long ttlMs;
        private final int baseLatencyMs;
        
        private final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();
        private long hits = 0;
        private long misses = 0;
        private String lastFetchSource = "";
        
        EdgeNode(String name, EdgeNode parent, OriginServer origin, 
                 long ttlMs, int baseLatencyMs) {
            this.name = name;
            this.parent = parent;
            this.origin = origin;
            this.ttlMs = ttlMs;
            this.baseLatencyMs = baseLatencyMs;
        }
        
        public String fetch(String url) {
            simulateLatency(baseLatencyMs);
            
            CacheEntry entry = cache.get(url);
            if (entry != null && !entry.isExpired()) {
                hits++;
                lastFetchSource = name + " (cache)";
                return entry.content;
            }
            
            misses++;
            String content;
            
            if (parent != null) {
                content = parent.fetch(url);
                lastFetchSource = parent.getLastFetchSource();
            } else if (origin != null) {
                content = origin.fetch(url);
                lastFetchSource = "origin";
            } else {
                return null;
            }
            
            if (content != null) {
                cache.put(url, new CacheEntry(content, ttlMs));
            }
            
            return content;
        }
        
        public void purge(String url) {
            cache.remove(url);
        }
        
        public String getLastFetchSource() {
            return lastFetchSource;
        }
        
        public String getStats() {
            long total = hits + misses;
            double hitRate = total > 0 ? (hits * 100.0 / total) : 0;
            return String.format("Hits: %d, Misses: %d, Hit Rate: %.1f%%", 
                               hits, misses, hitRate);
        }
        
        private void simulateLatency(int ms) {
            try {
                Thread.sleep(ms);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
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
