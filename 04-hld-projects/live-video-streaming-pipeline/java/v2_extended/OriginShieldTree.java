package v2_extended;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;

/**
 * v2-extended live video streaming pipeline.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Flash-crowd request collapsing with bounded cache tiers and origin
 *    metrics (FOLLOW-UPS.md #2, PITFALLS.md #2): concurrent misses for
 *    the same segment collapse into one origin load (singleflight), each
 *    cache tier is bounded with LRU eviction, and origin reads are
 *    counted so origin load is observable.
 *
 * 2. Transcoder node failure recovery with time-aligned keyframes
 *    (FOLLOW-UPS.md #1, PITFALLS.md #4): see AbrTranscoderLadder.
 *
 * 3. Live-to-VOD archival (FOLLOW-UPS.md #4): see LiveManifestManager.
 */
public class OriginShieldTree {

    /** Bounded LRU tier; oldest entry evicted past maxEntries. */
    private static class LruTier {
        private final int maxEntries; // -1 means unbounded (v1 behavior)
        private final Map<String, String> map = new LinkedHashMap<>(16, 0.75f, true);

        LruTier(int maxEntries) {
            this.maxEntries = maxEntries;
        }

        synchronized String get(String key) {
            return map.get(key); // access-order LinkedHashMap touches on get
        }

        synchronized void put(String key, String value) {
            map.put(key, value);
            while (maxEntries >= 0 && map.size() > maxEntries) {
                String eldest = map.keySet().iterator().next();
                map.remove(eldest);
            }
        }

        synchronized boolean contains(String key) {
            return map.containsKey(key);
        }

        synchronized int size() {
            return map.size();
        }
    }

    private final LruTier l1Cache;
    private final LruTier l2Cache;
    private final Map<String, String> origin = new ConcurrentHashMap<>();
    private final Function<String, String> originLoader; // nullable
    private final AtomicInteger originReads = new AtomicInteger(0);
    private final Map<String, Object> keyMonitors = new ConcurrentHashMap<>();

    public OriginShieldTree() {
        this(-1, null);
    }

    public OriginShieldTree(int maxTierEntries) {
        this(maxTierEntries, null);
    }

    public OriginShieldTree(int maxTierEntries, Function<String, String> originLoader) {
        this.l1Cache = new LruTier(maxTierEntries);
        this.l2Cache = new LruTier(maxTierEntries);
        this.originLoader = originLoader;
    }

    public void writeToOrigin(String key, String value) {
        origin.put(key, value);
    }

    public int getOriginReads() {
        return originReads.get();
    }

    public int l1Size() {
        return l1Cache.size();
    }

    public String fetch(String key) {
        // Fast path: already cached.
        String val = l1Cache.get(key);
        if (val != null) {
            return val;
        }
        val = l2Cache.get(key);
        if (val != null) {
            l1Cache.put(key, val);
            return val;
        }

        // Singleflight: concurrent misses for the same key collapse into
        // one origin load (PITFALLS.md #2: the origin should see a handful
        // of requests, not one per viewer).
        Object monitor = keyMonitors.computeIfAbsent(key, k -> new Object());
        synchronized (monitor) {
            val = l1Cache.get(key);
            if (val == null) {
                val = l2Cache.get(key);
            }
            if (val != null) {
                l1Cache.put(key, val);
                return val;
            }

            originReads.incrementAndGet();
            val = originLoader != null ? originLoader.apply(key) : origin.get(key);
            if (val == null) {
                return null;
            }
            l2Cache.put(key, val);
            l1Cache.put(key, val);
            return val;
        }
    }

    /** Test hook: whether a key currently sits in L1. */
    public boolean l1Contains(String key) {
        return l1Cache.contains(key);
    }
}
