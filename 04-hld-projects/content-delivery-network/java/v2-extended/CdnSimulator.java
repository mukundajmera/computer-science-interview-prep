package v2_extended;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.function.LongSupplier;

/**
 * v2-extended CDN simulator.
 *
 * Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 1. Cache-key normalization at the edge (PITFALLS #6, FOLLOW-UPS #3):
 *    non-whitelisted query parameters are stripped and the key is
 *    Customer_ID + normalized path, so random cache-busters like ?cb=123
 *    can no longer bypass the cache and flood the customer origin.
 * 2. TTL expiry with stale-on-error (PITFALLS #7): edge entries carry a TTL;
 *    expired entries are revalidated, and while the origin errors, entries
 *    still inside the stale window are served instead of failing the request
 *    (the synchronous analog of stale-while-revalidate).
 * 3. Bounded LRU edge cache (PITFALLS #2 and the v2 "expiry or eviction"
 *    weakness): the edge cache evicts the least-recently-used entry once it
 *    exceeds maxEntries instead of growing without bound.
 */
public class CdnSimulator {

    /** The customer origin is unreachable or erroring (injectable in tests). */
    public static class OriginError extends RuntimeException {
        public OriginError(String message) {
            super(message);
        }
    }

    /**
     * Build the cache key: customerId + path + whitelisted, sorted params.
     * Parameters not in allowedParams are dropped, so /a?cb=123 and /a?cb=456
     * share one cache entry. With an empty whitelist, all parameters are stripped.
     */
    public static String normalizeKey(String path, String customerId,
                                      List<String> allowedParams) {
        List<String> allowed = allowedParams == null ? new ArrayList<>() : allowedParams;
        String base = path;
        String query = null;
        int q = path.indexOf('?');
        if (q >= 0) {
            base = path.substring(0, q);
            query = path.substring(q + 1);
        }
        TreeSet<String> kept = new TreeSet<>();
        if (query != null && !query.isEmpty()) {
            for (String pair : query.split("&")) {
                String name = pair;
                int eq = pair.indexOf('=');
                if (eq >= 0) {
                    name = pair.substring(0, eq);
                }
                if (!name.isEmpty() && allowed.contains(name)) {
                    kept.add(pair);
                }
            }
        }
        String normalized = kept.isEmpty() ? base : base + "?" + String.join("&", kept);
        return customerId + ":" + normalized;
    }

    private static class CacheEntry {
        final String value;
        final long storedAt;

        CacheEntry(String value, long storedAt) {
            this.value = value;
            this.storedAt = storedAt;
        }
    }

    public static class CustomerOrigin {
        private final Map<String, String> dataStore = new LinkedHashMap<>();
        public int fetchCount = 0;
        public boolean fail = false;

        public void put(String path, String data) {
            dataStore.put(path, data);
        }

        public String fetch(String path) {
            fetchCount++;
            if (fail) {
                throw new OriginError("origin unreachable");
            }
            return dataStore.get(path);
        }
    }

    /** Same coalescing semantics as v1; keyed by the normalized path it
     *  receives from the edge. */
    public static class OriginShield {
        private final CustomerOrigin origin;
        private final Map<String, String> cache = new LinkedHashMap<>();
        private final Map<String, List<Object>> inFlightRequests = new LinkedHashMap<>();
        public int cacheHitCount = 0;
        public int fetchCount = 0;

        public OriginShield(CustomerOrigin origin) {
            this.origin = origin;
        }

        public String fetch(String path) {
            fetchCount++;
            if (cache.containsKey(path)) {
                cacheHitCount++;
                return cache.get(path);
            }

            if (inFlightRequests.containsKey(path)) {
                return "COALESCED";
            }

            inFlightRequests.put(path, new ArrayList<>());
            String data;
            try {
                data = origin.fetch(path);
            } finally {
                // Always release the in-flight marker, even when the origin
                // errors, or later fetches would be coalesced forever.
                inFlightRequests.remove(path);
            }
            if (data != null) {
                cache.put(path, data);
            }
            return data;
        }

        public void simulateConcurrentFetches(String path, int numRequests, List<String> results) {
            fetchCount += numRequests;
            if (cache.containsKey(path)) {
                cacheHitCount += numRequests;
                for (int i = 0; i < numRequests; i++) {
                    results.add(cache.get(path));
                }
                return;
            }

            String data = origin.fetch(path);
            if (data != null) {
                cache.put(path, data);
            }
            for (int i = 0; i < numRequests; i++) {
                results.add(data);
            }
        }

        public void clearCache() {
            cache.clear();
        }
    }

    public static class EdgeNode {
        private final OriginShield shield;
        private final long ttlMillis;
        private final long staleWindowMillis;
        private final int maxEntries;
        private final LongSupplier clock;
        private final Map<String, CacheEntry> cache;
        public int cacheHitCount = 0;
        public int staleServedCount = 0;

        public EdgeNode(OriginShield shield, long ttlMillis, long staleWindowMillis,
                        int maxEntries, LongSupplier clock) {
            if (ttlMillis < 0) {
                throw new IllegalArgumentException("ttlMillis must be >= 0");
            }
            if (staleWindowMillis < 0) {
                throw new IllegalArgumentException("staleWindowMillis must be >= 0");
            }
            if (maxEntries < 1) {
                throw new IllegalArgumentException("maxEntries must be >= 1");
            }
            this.shield = shield;
            this.ttlMillis = ttlMillis;
            this.staleWindowMillis = staleWindowMillis;
            this.maxEntries = maxEntries;
            this.clock = clock;
            this.cache = new LinkedHashMap<String, CacheEntry>(16, 0.75f, true);
        }

        public EdgeNode(OriginShield shield) {
            this(shield, 60000L, 300000L, 10000, System::currentTimeMillis);
        }

        public int cacheSize() {
            return cache.size();
        }

        public boolean containsKey(String key) {
            return cache.containsKey(key);
        }

        private String lookupFresh(String key) {
            CacheEntry entry = cache.get(key); // access-order LinkedHashMap: a get refreshes recency
            if (entry == null) {
                return null;
            }
            if (clock.getAsLong() - entry.storedAt <= ttlMillis) {
                cacheHitCount++;
                return entry.value;
            }
            return null;
        }

        private void store(String key, String data) {
            cache.put(key, new CacheEntry(data, clock.getAsLong()));
            while (cache.size() > maxEntries) {
                String eldest = cache.keySet().iterator().next();
                cache.remove(eldest); // evict least-recently-used
            }
        }

        public String fetch(String path, String customerId, List<String> allowedParams) {
            String key = normalizeKey(path, customerId, allowedParams);

            String fresh = lookupFresh(key);
            if (fresh != null) {
                return fresh;
            }

            String normalizedPath = key.split(":", 2)[1];
            CacheEntry entry = cache.get(key);
            String data;
            try {
                data = shield.fetch(normalizedPath);
            } catch (OriginError error) {
                // Stale-on-error: serve the expired entry if it is still inside
                // the stale window instead of failing the request (PITFALLS #7).
                if (entry != null
                        && clock.getAsLong() - entry.storedAt <= ttlMillis + staleWindowMillis) {
                    staleServedCount++;
                    return entry.value;
                }
                throw error;
            }
            if (data != null && !data.equals("COALESCED")) {
                store(key, data);
            }
            return data;
        }

        public String fetch(String path) {
            return fetch(path, "default", new ArrayList<>());
        }

        public void fetchBatch(String path, int count, List<String> results,
                               String customerId, List<String> allowedParams) {
            String key = normalizeKey(path, customerId, allowedParams);
            String fresh = lookupFresh(key);
            if (fresh != null) {
                for (int i = 0; i < count; i++) {
                    results.add(fresh);
                }
                return;
            }

            String normalizedPath = key.split(":", 2)[1];
            shield.simulateConcurrentFetches(normalizedPath, count, results);
            if (!results.isEmpty() && results.get(0) != null) {
                store(key, results.get(0));
            }
        }

        public void purge(String path, String customerId, List<String> allowedParams) {
            cache.remove(normalizeKey(path, customerId, allowedParams));
        }
    }
}
