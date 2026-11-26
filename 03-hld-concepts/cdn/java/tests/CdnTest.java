import java.util.HashMap;
import java.util.Map;

/**
 * Tests for CDN implementations.
 */
public class CdnTest {
    
    public static void main(String[] args) throws Exception {
        System.out.println("Running tests...");
        simpleCache_shouldCacheOnSecondRequest();
        simpleCache_shouldPurgeCorrectly();
        simpleCache_shouldTrackHitRate();
        geoCdn_shouldRouteToCorrectEdge();
        geoCdn_shieldShouldCacheForAllEdges();
        geoCdn_globalPurgeShouldClearAllEdges();
        productionCdn_shouldParseCacheControl();
        productionCdn_noCacheShouldBypassCache();
        productionCdn_shouldTrackMetrics();
        productionCdn_metricsZeroRequests();
        productionCdn_metricsPurgeTracking();
        productionCdn_wildcardPurgeShouldWork();
        System.out.println("All tests passed.");
    }
    
    private static void assertEquals(Object expected, Object actual) {
        if (expected == null && actual == null) return;
        if (expected != null && expected.equals(actual)) return;
        throw new AssertionError("Expected " + expected + " but got " + actual);
    }

    private static void assertEquals(double expected, double actual, double delta) {
        if (Math.abs(expected - actual) <= delta) return;
        throw new AssertionError("Expected " + expected + " but got " + actual);
    }
    
    private static void assertTrue(boolean condition) {
        if (!condition) throw new AssertionError("Expected true but was false");
    }
    
    private static void assertFalse(boolean condition) {
        if (condition) throw new AssertionError("Expected false but was true");
    }

    // ==================== SimpleProxyCache Tests ====================
    
    static void simpleCache_shouldCacheOnSecondRequest() {
        int[] fetchCount = {0};
        SimpleProxyCache.OriginServer origin = url -> {
            fetchCount[0]++;
            return "content-" + url;
        };
        
        SimpleProxyCache cache = new SimpleProxyCache(origin, 60000);
        
        String result1 = cache.fetch("/test.html");
        String result2 = cache.fetch("/test.html");
        
        assertEquals(result1, result2);
        assertEquals(1, fetchCount[0]); // Only one origin fetch
    }
    
    static void simpleCache_shouldPurgeCorrectly() {
        int[] fetchCount = {0};
        SimpleProxyCache.OriginServer origin = url -> {
            fetchCount[0]++;
            return "content-" + fetchCount[0];
        };
        
        SimpleProxyCache cache = new SimpleProxyCache(origin, 60000);
        
        cache.fetch("/test.html");
        cache.purge("/test.html");
        String result = cache.fetch("/test.html");
        
        assertEquals("content-2", result);
        assertEquals(2, fetchCount[0]);
    }
    
    static void simpleCache_shouldTrackHitRate() {
        SimpleProxyCache.OriginServer origin = url -> "content";
        SimpleProxyCache cache = new SimpleProxyCache(origin, 60000);
        
        cache.fetch("/a"); // miss
        cache.fetch("/a"); // hit
        cache.fetch("/a"); // hit
        cache.fetch("/b"); // miss
        
        assertEquals(50.0, cache.getHitRate(), 0.1);
    }
    
    // ==================== GeographicCDN Tests ====================
    
    static void geoCdn_shouldRouteToCorrectEdge() {
        GeographicCDN.OriginServer origin = url -> "content";
        GeographicCDN cdn = new GeographicCDN(origin, 60000, 30000);
        
        GeographicCDN.EdgeNode japanEdge = cdn.routeToEdge("japan");
        GeographicCDN.EdgeNode germanyEdge = cdn.routeToEdge("germany");
        GeographicCDN.EdgeNode californiaEdge = cdn.routeToEdge("california");
        
        assertEquals("asia-east", japanEdge.name);
        assertEquals("eu-west", germanyEdge.name);
        assertEquals("us-west", californiaEdge.name);
    }
    
    static void geoCdn_shieldShouldCacheForAllEdges() {
        int[] originCalls = {0};
        GeographicCDN.OriginServer origin = url -> {
            originCalls[0]++;
            return "content-" + originCalls[0];
        };
        
        GeographicCDN cdn = new GeographicCDN(origin, 60000, 30000);
        
        cdn.fetch("japan", "/video.mp4");
        cdn.fetch("germany", "/video.mp4");
        
        // Only one origin call (shield cached it)
        assertEquals(1, originCalls[0]);
    }
    
    static void geoCdn_globalPurgeShouldClearAllEdges() {
        int[] originCalls = {0};
        GeographicCDN.OriginServer origin = url -> {
            originCalls[0]++;
            return "content-" + originCalls[0];
        };
        
        GeographicCDN cdn = new GeographicCDN(origin, 60000, 30000);
        
        cdn.fetch("japan", "/video.mp4");
        cdn.fetch("germany", "/video.mp4");
        
        cdn.purgeGlobal("/video.mp4");
        
        cdn.fetch("japan", "/video.mp4");
        
        assertEquals(2, originCalls[0]);
    }
    
    // ==================== ProductionCDN Tests ====================
    
    static void productionCdn_shouldParseCacheControl() {
        ProductionCDN.CacheControl cc = ProductionCDN.CacheControl.parse(
            "max-age=300, stale-while-revalidate=60");
        
        assertEquals(300, cc.maxAgeSeconds);
        assertEquals(60, cc.staleWhileRevalidateSeconds);
        assertFalse(cc.noCache);
    }
    
    static void productionCdn_noCacheShouldBypassCache() {
        int[] fetchCount = {0};
        ProductionCDN.OriginServer origin = url -> {
            fetchCount[0]++;
            return "content-" + fetchCount[0];
        };
        
        ProductionCDN cdn = new ProductionCDN(origin);
        
        Map<String, String> defaultHeaders = new HashMap<>();
        Map<String, String> noCacheHeaders = new HashMap<>();
        noCacheHeaders.put("Cache-Control", "no-cache");
        
        cdn.fetch("japan", "/api/data", defaultHeaders);
        cdn.fetch("japan", "/api/data", noCacheHeaders);
        
        assertEquals(2, fetchCount[0]);
        cdn.shutdown();
    }
    
    static void productionCdn_shouldTrackMetrics() {
        ProductionCDN.OriginServer origin = url -> "content";
        ProductionCDN cdn = new ProductionCDN(origin);
        
        Map<String, String> headers = new HashMap<>();
        
        cdn.fetch("japan", "/a", headers); // miss
        cdn.fetch("japan", "/a", headers); // hit
        cdn.fetch("japan", "/b", headers); // miss
        
        double hitRate = cdn.getMetrics().getHitRate();
        assertTrue(hitRate > 30 && hitRate < 40);
        
        cdn.shutdown();
    }
    
    static void productionCdn_metricsZeroRequests() {
        ProductionCDN.OriginServer origin = url -> "content";
        ProductionCDN cdn = new ProductionCDN(origin);
        
        assertEquals(0.0, cdn.getMetrics().getHitRate(), 0.001);
        assertEquals(0.0, cdn.getMetrics().getAverageLatencyMs(), 0.001);
        
        cdn.shutdown();
    }
    
    static void productionCdn_metricsPurgeTracking() throws Exception {
        ProductionCDN.OriginServer origin = url -> "content";
        ProductionCDN cdn = new ProductionCDN(origin);
        
        Map<String, String> headers = new HashMap<>();
        cdn.fetch("japan", "/a", headers);
        cdn.purge("/a").get();
        
        String metricsStr = cdn.getMetrics().toString();
        assertTrue(metricsStr.contains("Purges=1"));
        
        cdn.shutdown();
    }
    
    static void productionCdn_wildcardPurgeShouldWork() throws Exception {
        ProductionCDN.OriginServer origin = url -> "content";
        ProductionCDN cdn = new ProductionCDN(origin);
        
        Map<String, String> headers = new HashMap<>();
        
        cdn.fetch("japan", "/images/a.jpg", headers);
        cdn.fetch("japan", "/images/b.jpg", headers);
        cdn.fetch("japan", "/videos/c.mp4", headers);
        
        cdn.purge("/images/*").get();
        
        ProductionCDN.CdnResponse r1 = cdn.fetch("japan", "/images/a.jpg", headers);
        ProductionCDN.CdnResponse r2 = cdn.fetch("japan", "/videos/c.mp4", headers);
        
        assertFalse(r1.cacheHit); // Purged
        assertTrue(r2.cacheHit);  // Still cached
        
        cdn.shutdown();
    }
}
