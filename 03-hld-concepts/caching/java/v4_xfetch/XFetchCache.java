package v4_xfetch;

import java.util.concurrent.*;
import java.util.function.Supplier;

/**
 * XFetchCache with Singleflight deduplication.
 * Uses probabilistic early expiration.
 */
public class XFetchCache {
    private final double beta;
    private final Supplier<Long> clock;
    private final Supplier<Double> rng;
    
    private final ConcurrentHashMap<Object, CacheEntry> store = new ConcurrentHashMap<>();
    private final SingleflightMutex sf = new SingleflightMutex();
    private final ExecutorService executor;

    public static class CacheEntry {
        public final Object value;
        public final long ttl;
        public final double delta;
        public final long createdAt;
        public final long expiresAt;

        public CacheEntry(Object value, long ttl, double delta, long createdAt) {
            this.value = value;
            this.ttl = ttl;
            this.delta = delta;
            this.createdAt = createdAt;
            this.expiresAt = createdAt + ttl;
        }
    }

    public XFetchCache(double beta, Supplier<Long> clock, Supplier<Double> rng, int executorWorkers) {
        this.beta = beta;
        this.clock = clock != null ? clock : System::currentTimeMillis;
        this.rng = rng != null ? rng : Math::random;
        this.executor = Executors.newFixedThreadPool(executorWorkers);
    }
    
    public XFetchCache() {
        this(1.0, null, null, 4);
    }

    private Object computeAndStore(Object key, Supplier<Object> loader, long ttlMs) {
        long start = clock.get();
        Object val = loader.get();
        long end = clock.get();
        
        double delta = Math.max(1.0, (double) (end - start));
        CacheEntry entry = new CacheEntry(val, ttlMs, delta, end);
        store.put(key, entry);
        return val;
    }

    private boolean shouldRefresh(CacheEntry entry, long now) {
        long remaining = entry.expiresAt - now;
        
        if (remaining <= 0) {
            return true; // Already logically expired
        }

        double u = rng.get();
        while (u == 0.0) {
            u = rng.get(); // u must be in (0, 1]
        }

        // XFetch probability: -beta * delta * ln(u) >= remaining
        double threshold = -beta * entry.delta * Math.log(u);
        return threshold >= remaining;
    }

    public Object get(Object key, Supplier<Object> loader, long ttlMs) {
        long now = clock.get();
        CacheEntry entry = store.get(key);

        if (entry == null) {
            // Miss: singleflight block and load
            SingleflightMutex.Result res = sf.doCall(key, () -> computeAndStore(key, loader, ttlMs));
            if (res.error != null) {
                throw new RuntimeException("Loader failed", res.error);
            }
            return res.value;
        }

        if (shouldRefresh(entry, now)) {
            // Probabilistic early expiration triggered
            // Refresh asynchronously in the background
            executor.submit(() -> {
                sf.doCall(key, () -> computeAndStore(key, loader, ttlMs));
            });
        }

        return entry.value;
    }

    public void shutdown() {
        executor.shutdownNow();
    }
    
    // Package-private for testing
    CacheEntry getEntry(Object key) {
        return store.get(key);
    }
}
