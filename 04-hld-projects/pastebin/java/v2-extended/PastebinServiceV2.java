import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * v2-extended pastebin service.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Burn-after-reading pastes (FOLLOW-UPS.md #2): a paste created with
 *    burnAfterReading=true is returned exactly once. The read and delete
 *    happen atomically under one write lock, so concurrent readers
 *    cannot both receive the content - the first wins, everyone else
 *    gets a 404-style miss. Burned pastes never enter the read cache.
 *
 * 2. Hot-key read cache with metrics (FOLLOW-UPS.md #1 viral paste): a
 *    small, short-lived in-memory LRU cache sits in front of the blob
 *    store, absorbing repeat reads of a viral paste the way the doc's
 *    5-second local cache on API servers does. Hits and misses are
 *    counted so the shielding effect is observable, and expired or
 *    deleted pastes are purged from the cache.
 *
 * 3. KGS-style key block allocation (FOLLOW-UPS.md #3): short-link ids
 *    come from a KeyBlockAllocatorV2 that hands out pre-allocated blocks
 *    of ids, the way a Key Generation Service pre-generates keys.
 *    Exhaustion is loud and explicit instead of a silent collision.
 */
public class PastebinServiceV2 {
    private final Map<String, PasteMetadataV2> metadataStore;
    private final Map<String, String> blobStore;
    private final Map<String, TokenBucket> rateLimiters;
    private final ReadWriteLock lock;
    private final KeyBlockAllocatorV2 keyAllocator;

    private final TtlCleanerV2 ttlCleaner;

    private final int capacity;
    private final double fillRate;

    // Improvement #2: hot-key read cache (short-lived LRU) + metrics.
    private final int readCacheMaxEntries;
    private final long readCacheTtlMs;
    private final Map<String, CacheEntry> readCache;
    private long readCacheHits = 0;
    private long readCacheMisses = 0;

    private static class CacheEntry {
        final String content;
        final long cachedAtMs;

        CacheEntry(String content, long cachedAtMs) {
            this.content = content;
            this.cachedAtMs = cachedAtMs;
        }
    }

    public PastebinServiceV2(int capacity, double fillRate) {
        this(capacity, fillRate, new KeyBlockAllocatorV2(), 128, 5000L);
    }

    public PastebinServiceV2(int capacity, double fillRate, KeyBlockAllocatorV2 keyAllocator,
                             int readCacheMaxEntries, long readCacheTtlMs) {
        this.metadataStore = new HashMap<>();
        this.blobStore = new HashMap<>();
        this.rateLimiters = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
        this.keyAllocator = keyAllocator;
        this.ttlCleaner = new TtlCleanerV2(metadataStore, blobStore, lock);
        this.capacity = capacity;
        this.fillRate = fillRate;
        this.readCacheMaxEntries = readCacheMaxEntries;
        this.readCacheTtlMs = readCacheTtlMs;
        // access-order LinkedHashMap = LRU
        this.readCache = new LinkedHashMap<>(16, 0.75f, true);
    }

    private TokenBucket getLimiter(String ipAddress) {
        lock.writeLock().lock();
        try {
            return rateLimiters.computeIfAbsent(ipAddress, k -> new TokenBucket(capacity, fillRate));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public String createPaste(String content, String ipAddress, Long ttlSeconds, boolean burnAfterReading) {
        TokenBucket limiter = getLimiter(ipAddress);
        if (!limiter.consume()) {
            return null; // Rate limit exceeded
        }

        long id = keyAllocator.nextId(); // throws KeyPoolExhausted when dry
        String shortLink = Base62EncoderV2.encode(id);
        while (shortLink.length() < 7) {
            shortLink = "0" + shortLink;
        }

        long nowMs = System.currentTimeMillis();
        Long expiresAtMs = ttlSeconds != null ? nowMs + (ttlSeconds * 1000) : null;

        PasteMetadataV2 metadata = new PasteMetadataV2(id, shortLink, nowMs, expiresAtMs, burnAfterReading);

        lock.writeLock().lock();
        try {
            metadataStore.put(shortLink, metadata);
            blobStore.put(shortLink, content);
        } finally {
            lock.writeLock().unlock();
        }

        return shortLink;
    }

    public String createPaste(String content, String ipAddress, Long ttlSeconds) {
        return createPaste(content, ipAddress, ttlSeconds, false);
    }

    public String createPaste(String content, String ipAddress) {
        return createPaste(content, ipAddress, null, false);
    }

    public String getPaste(String shortLink) {
        lock.writeLock().lock();
        try {
            PasteMetadataV2 metadata = metadataStore.get(shortLink);
            if (metadata == null) {
                return null;
            }

            if (metadata.getExpiresAtMs() != null && System.currentTimeMillis() > metadata.getExpiresAtMs()) {
                // Active TTL validation on read
                deletePaste(shortLink);
                return null;
            }

            // Improvement #1: burn-after-reading - atomic read + delete so
            // only one reader ever receives the content. Never cached.
            if (metadata.isBurnAfterReading()) {
                String content = blobStore.get(shortLink);
                deletePaste(shortLink);
                return content;
            }

            // Improvement #2: serve viral pastes from the hot-key cache.
            CacheEntry cached = readCache.get(shortLink);
            if (cached != null) {
                if (System.currentTimeMillis() - cached.cachedAtMs <= readCacheTtlMs) {
                    readCacheHits++;
                    return cached.content;
                }
                readCache.remove(shortLink);
            }
            readCacheMisses++;
            String content = blobStore.get(shortLink);
            if (content != null) {
                readCache.put(shortLink, new CacheEntry(content, System.currentTimeMillis()));
                while (readCache.size() > readCacheMaxEntries) {
                    String eldest = readCache.keySet().iterator().next();
                    readCache.remove(eldest);
                }
            }
            return content;
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void deletePaste(String shortLink) {
        metadataStore.remove(shortLink);
        blobStore.remove(shortLink);
        readCache.remove(shortLink);
    }

    public int sweepExpiredPastes() {
        List<String> swept = ttlCleaner.sweep();
        if (!swept.isEmpty()) {
            lock.writeLock().lock();
            try {
                for (String shortLink : swept) {
                    readCache.remove(shortLink);
                }
            } finally {
                lock.writeLock().unlock();
            }
        }
        return swept.size();
    }

    public long getReadCacheHits() {
        return readCacheHits;
    }

    public long getReadCacheMisses() {
        return readCacheMisses;
    }

    /** Test hook: whether a link currently sits in the read cache. */
    public boolean readCacheContains(String shortLink) {
        lock.readLock().lock();
        try {
            return readCache.containsKey(shortLink);
        } finally {
            lock.readLock().unlock();
        }
    }

    private static class TokenBucket {
        private final int capacity;
        private final double fillRate;
        private double tokens;
        private long lastFillMs;

        public TokenBucket(int capacity, double fillRate) {
            this.capacity = capacity;
            this.fillRate = fillRate;
            this.tokens = capacity;
            this.lastFillMs = System.currentTimeMillis();
        }

        public synchronized boolean consume() {
            long nowMs = System.currentTimeMillis();
            double elapsedSeconds = (nowMs - lastFillMs) / 1000.0;

            tokens = Math.min(capacity, tokens + elapsedSeconds * fillRate);
            lastFillMs = nowMs;

            if (tokens >= 1.0) {
                tokens -= 1.0;
                return true;
            }
            return false;
        }
    }
}
