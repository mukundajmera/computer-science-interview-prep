import v2_extended.CdnSimulator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class CdnSimulatorV2Test {

    private static class FakeClock implements java.util.function.LongSupplier {
        long now = 1_000_000L;
        public long getAsLong() { return now; }
        void advance(long millis) { now += millis; }
    }

    public static void main(String[] args) {
        testNormalHit();
        testThunderingHerdCoalescing();
        testRandomQueryBustersShareOneCacheEntry();
        testAllParamsStrippedWithoutWhitelist();
        testWhitelistedParamsDistinguishEntriesSorted();
        testCustomerIdSeparatesCacheKeys();
        testTtlExpiryTriggersRevalidation();
        testStaleOnErrorServesExpiredEntry();
        testBeyondStaleWindowPropagatesOriginError();
        testOriginErrorWithoutEntryPropagates();
        testOriginErrorReleasesInFlightMarker();
        testLruEvictionBoundsCacheSize();
        testFreshHitRefreshesLruRecency();
        testPurgeUsesNormalizedKey();
        testInvalidPolicyValuesRejected();
        System.out.println("All Java CDN V2 tests passed!");
    }

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new RuntimeException(message);
        }
    }

    private static CdnSimulator.EdgeNode build(CdnSimulator.CustomerOrigin origin,
                                               CdnSimulator.OriginShield shield,
                                               long ttlMillis, long staleWindowMillis,
                                               int maxEntries,
                                               java.util.function.LongSupplier clock) {
        return new CdnSimulator.EdgeNode(shield, ttlMillis, staleWindowMillis, maxEntries, clock);
    }

    // --- v1 parity -----------------------------------------------------------

    private static void testNormalHit() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/images/logo.png", "binary_data_123");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(shield);

        String result1 = edge.fetch("/images/logo.png");
        check("binary_data_123".equals(result1), "Expected binary_data_123");
        check(origin.fetchCount == 1, "Expected 1 origin fetch");

        String result2 = edge.fetch("/images/logo.png");
        check("binary_data_123".equals(result2), "Expected binary_data_123");
        check(edge.cacheHitCount == 1, "Expected 1 edge cache hit");
        check(origin.fetchCount == 1, "Origin should not be hit again");
    }

    private static void testThunderingHerdCoalescing() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/videos/viral.mp4", "video_data_999");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(shield);

        List<String> results = new ArrayList<>();
        edge.fetchBatch("/videos/viral.mp4", 10000, results, "default", new ArrayList<>());

        check(results.size() == 10000, "Expected 10000 results");
        for (String res : results) {
            check("video_data_999".equals(res), "Expected video_data_999");
        }
        check(origin.fetchCount == 1, "Expected exactly 1 origin fetch, got " + origin.fetchCount);
        check(shield.fetchCount == 10000, "Shield should receive all 10000 requests");
    }

    // --- v2 item 1: cache-key normalization ----------------------------------

    private static void testRandomQueryBustersShareOneCacheEntry() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(new CdnSimulator.OriginShield(origin));

        check("data-a".equals(edge.fetch("/a?cb=123")), "First buster fetch failed");
        check("data-a".equals(edge.fetch("/a?cb=456")), "Second buster fetch failed");
        // The second fetch was an edge hit: the random buster did not bypass.
        check(origin.fetchCount == 1, "Expected 1 origin fetch, got " + origin.fetchCount);
        check(edge.cacheHitCount == 1, "Expected 1 edge cache hit");
    }

    private static void testAllParamsStrippedWithoutWhitelist() {
        String key1 = CdnSimulator.normalizeKey("/a?x=1&y=2", "default", new ArrayList<>());
        String key2 = CdnSimulator.normalizeKey("/a", "default", new ArrayList<>());
        check(key1.equals(key2), "Params were not stripped");
        check("default:/a".equals(key1), "Unexpected key: " + key1);
    }

    private static void testWhitelistedParamsDistinguishEntriesSorted() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a?v=1", "data-v1");
        origin.put("/a?v=2", "data-v2");
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(new CdnSimulator.OriginShield(origin));
        List<String> allowed = Arrays.asList("v");

        check("data-v1".equals(edge.fetch("/a?v=1&cb=x", "default", allowed)), "v=1 fetch failed");
        check("data-v2".equals(edge.fetch("/a?v=2&cb=y", "default", allowed)), "v=2 fetch failed");
        check(origin.fetchCount == 2, "Expected 2 origin fetches, got " + origin.fetchCount);
        // Sorted param order makes /a?v=1 and /a?cb=z&v=1 equivalent.
        check("data-v1".equals(edge.fetch("/a?cb=z&v=1", "default", allowed)), "Reordered fetch failed");
        check(origin.fetchCount == 2, "Reordered params should share the entry");
    }

    private static void testCustomerIdSeparatesCacheKeys() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(shield);

        edge.fetch("/a", "cust-1", new ArrayList<>());
        edge.fetch("/a", "cust-2", new ArrayList<>());
        // Two distinct edge entries were filled through the shield; the shield
        // is shared across tenants, so the origin was hit only once.
        check(origin.fetchCount == 1, "Expected 1 origin fetch, got " + origin.fetchCount);
        check(shield.fetchCount == 2, "Expected 2 shield fetches, got " + shield.fetchCount);
        check(edge.containsKey("cust-1:/a"), "cust-1 entry missing");
        check(edge.containsKey("cust-2:/a"), "cust-2 entry missing");
    }

    // --- v2 item 2: TTL expiry + stale-on-error ------------------------------

    private static void testTtlExpiryTriggersRevalidation() {
        FakeClock clock = new FakeClock();
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = build(origin, shield, 10000L, 100000L, 1000, clock);

        edge.fetch("/a");
        check(origin.fetchCount == 1, "Expected 1 origin fetch");
        clock.advance(11000L);
        // The shield still caches, so revalidation does not reach the origin.
        edge.fetch("/a");
        check(edge.staleServedCount == 0, "No stale serve expected while shield healthy");
    }

    private static void testStaleOnErrorServesExpiredEntry() {
        FakeClock clock = new FakeClock();
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = build(origin, shield, 10000L, 100000L, 1000, clock);

        edge.fetch("/a");
        shield.clearCache(); // force the next revalidation to reach the origin
        origin.fail = true;
        clock.advance(11000L); // past ttl, inside stale window
        check("data-a".equals(edge.fetch("/a")), "Expected stale data while origin down");
        check(edge.staleServedCount == 1, "Expected 1 stale serve");
    }

    private static void testBeyondStaleWindowPropagatesOriginError() {
        FakeClock clock = new FakeClock();
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = build(origin, shield, 10000L, 100000L, 1000, clock);

        edge.fetch("/a");
        shield.clearCache();
        origin.fail = true;
        clock.advance(111000L); // past ttl + stale window
        expectOriginError(() -> edge.fetch("/a"));
    }

    private static void testOriginErrorWithoutEntryPropagates() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.fail = true;
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(new CdnSimulator.OriginShield(origin));
        expectOriginError(() -> edge.fetch("/missing"));
    }

    private static void testOriginErrorReleasesInFlightMarker() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);

        origin.fail = true;
        try {
            shield.fetch("/a");
            throw new RuntimeException("Expected OriginError");
        } catch (CdnSimulator.OriginError expected) {
            // expected
        }
        origin.fail = false;
        // If the marker leaked, this fetch would return "COALESCED" forever.
        check("data-a".equals(shield.fetch("/a")), "In-flight marker was not released");
    }

    // --- v2 item 3: bounded LRU eviction -------------------------------------

    private static void testLruEvictionBoundsCacheSize() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = build(origin, shield, 60000L, 300000L, 2, System::currentTimeMillis);
        for (String name : Arrays.asList("/a", "/b", "/c")) {
            origin.put(name, "data" + name);
            edge.fetch(name);
        }

        check(edge.cacheSize() == 2, "Expected cache size 2, got " + edge.cacheSize());
        check(!edge.containsKey("default:/a"), "Oldest entry should be evicted");
        edge.fetch("/a");
        // The eviction forced a shield round-trip; the shared shield cache
        // still protects the origin, which stays at 3 fetches.
        check(shield.fetchCount == 4, "Expected 4 shield fetches, got " + shield.fetchCount);
        check(origin.fetchCount == 3, "Expected 3 origin fetches, got " + origin.fetchCount);
    }

    private static void testFreshHitRefreshesLruRecency() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = build(origin, shield, 60000L, 300000L, 2, System::currentTimeMillis);
        origin.put("/a", "data/a");
        origin.put("/b", "data/b");
        edge.fetch("/a");
        edge.fetch("/b");
        edge.fetch("/a"); // hit: /a becomes most-recently-used
        origin.put("/c", "data/c");
        edge.fetch("/c");

        check(edge.containsKey("default:/a"), "/a should still be cached");
        check(!edge.containsKey("default:/b"), "/b should be evicted instead");
    }

    // --- edges ----------------------------------------------------------------

    private static void testPurgeUsesNormalizedKey() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/a", "data-a");
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(shield);

        edge.fetch("/a?cb=1");
        edge.purge("/a?cb=2", "default", new ArrayList<>()); // same normalized entry
        edge.fetch("/a");
        // The purge really removed the edge entry: the request went back to
        // the shield (fetch 2), which served it without touching the origin.
        check(shield.fetchCount == 2, "Expected 2 shield fetches, got " + shield.fetchCount);
        check(origin.fetchCount == 1, "Expected 1 origin fetch, got " + origin.fetchCount);
    }

    private static void testInvalidPolicyValuesRejected() {
        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(new CdnSimulator.CustomerOrigin());
        expectIllegalArgument(() -> new CdnSimulator.EdgeNode(shield, -1L, 300000L, 1000, System::currentTimeMillis));
        expectIllegalArgument(() -> new CdnSimulator.EdgeNode(shield, 60000L, -1L, 1000, System::currentTimeMillis));
        expectIllegalArgument(() -> new CdnSimulator.EdgeNode(shield, 60000L, 300000L, 0, System::currentTimeMillis));
    }

    private static void expectOriginError(Runnable action) {
        try {
            action.run();
        } catch (CdnSimulator.OriginError expected) {
            return;
        }
        throw new RuntimeException("Expected OriginError");
    }

    private static void expectIllegalArgument(Runnable action) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new RuntimeException("Expected IllegalArgumentException");
    }
}
