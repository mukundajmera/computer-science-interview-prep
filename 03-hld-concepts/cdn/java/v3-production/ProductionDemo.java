import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Demo for ProductionCDN
 */
public class ProductionDemo {
    
    public static void main(String[] args) throws Exception {
        System.out.println("=== Production CDN Demo ===\n");
        
        // Create origin with latency
        ProductionCDN.OriginServer origin = url -> {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "Content: " + url + " @ " + System.currentTimeMillis();
        };
        
        ProductionCDN cdn = new ProductionCDN(origin);
        
        // 1. Basic caching
        System.out.println("=== Basic Caching ===");
        Map<String, String> defaultHeaders = new HashMap<>();
        
        ProductionCDN.CdnResponse r1 = cdn.fetch("japan", "/video/movie.mp4", defaultHeaders);
        System.out.println("Request 1 (cold): " + r1);
        
        ProductionCDN.CdnResponse r2 = cdn.fetch("japan", "/video/movie.mp4", defaultHeaders);
        System.out.println("Request 2 (warm): " + r2);
        
        // 2. Cache-Control headers
        System.out.println("\n=== Cache-Control Headers ===");
        Map<String, String> shortTtl = new HashMap<>();
        shortTtl.put("Cache-Control", "max-age=5, stale-while-revalidate=10");
        
        ProductionCDN.CdnResponse r3 = cdn.fetch("germany", "/api/data.json", shortTtl);
        System.out.println("With short TTL: " + r3);
        
        // 3. no-cache directive
        Map<String, String> noCache = new HashMap<>();
        noCache.put("Cache-Control", "no-cache");
        
        ProductionCDN.CdnResponse r4 = cdn.fetch("japan", "/video/movie.mp4", noCache);
        System.out.println("With no-cache: " + r4);
        
        // 4. Global routing
        System.out.println("\n=== Geographic Routing ===");
        String[] regions = {"japan", "germany", "california", "india", "uk"};
        for (String region : regions) {
            ProductionCDN.CdnResponse r = cdn.fetch(region, "/global/asset.js", defaultHeaders);
            System.out.printf("User %-12s -> %s%n", region, r);
        }
        
        // 5. Cache warming
        System.out.println("\n=== Cache Warming ===");
        String warmUrl = "/launch/new-feature.js";
        System.out.println("Warming cache for: " + warmUrl);
        cdn.warmCache(warmUrl).get();
        System.out.println("Cache warmed across all edges");
        
        // All regions should now have cache hit
        for (String region : regions) {
            ProductionCDN.CdnResponse r = cdn.fetch(region, warmUrl, defaultHeaders);
            System.out.printf("User %-12s -> CacheHit: %s%n", region, r.cacheHit);
        }
        
        // 6. Purge API
        System.out.println("\n=== Purge API ===");
        CompletableFuture<ProductionCDN.PurgeResult> purgeFuture = cdn.purge("/video/*");
        ProductionCDN.PurgeResult purgeResult = purgeFuture.get();
        System.out.println(purgeResult);
        
        // After purge - cache miss
        ProductionCDN.CdnResponse r5 = cdn.fetch("japan", "/video/movie.mp4", defaultHeaders);
        System.out.println("After purge: " + r5);
        
        // 7. Metrics
        System.out.println("\n=== CDN Metrics ===");
        System.out.println(cdn.getMetrics());
        
        cdn.shutdown();
    }
}
