import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class PastebinService {
    private final Map<String, PasteMetadata> metadataStore;
    private final Map<String, String> blobStore;
    private final Map<String, TokenBucket> rateLimiters;
    private final ReadWriteLock lock;
    private final AtomicLong nextId;
    
    private final TtlCleaner ttlCleaner;

    private final int capacity;
    private final double fillRate;

    public PastebinService(int capacity, double fillRate) {
        this.metadataStore = new HashMap<>();
        this.blobStore = new HashMap<>();
        this.rateLimiters = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
        this.nextId = new AtomicLong(1000000000L); // Start large to get 6-7 char strings
        this.ttlCleaner = new TtlCleaner(metadataStore, blobStore, lock);
        this.capacity = capacity;
        this.fillRate = fillRate;
    }

    private TokenBucket getLimiter(String ipAddress) {
        lock.writeLock().lock();
        try {
            return rateLimiters.computeIfAbsent(ipAddress, k -> new TokenBucket(capacity, fillRate));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public String createPaste(String content, String ipAddress, Long ttlSeconds) {
        TokenBucket limiter = getLimiter(ipAddress);
        if (!limiter.consume()) {
            return null; // Rate limit exceeded
        }

        long id = nextId.getAndIncrement();
        String shortLink = Base62Encoder.encode(id);
        while (shortLink.length() < 7) {
            shortLink = "0" + shortLink;
        }

        long nowMs = System.currentTimeMillis();
        Long expiresAtMs = ttlSeconds != null ? nowMs + (ttlSeconds * 1000) : null;
        
        PasteMetadata metadata = new PasteMetadata(id, shortLink, nowMs, expiresAtMs);

        lock.writeLock().lock();
        try {
            metadataStore.put(shortLink, metadata);
            blobStore.put(shortLink, content);
        } finally {
            lock.writeLock().unlock();
        }

        return shortLink;
    }
    
    public String createPaste(String content, String ipAddress) {
        return createPaste(content, ipAddress, null);
    }

    public String getPaste(String shortLink) {
        lock.writeLock().lock();
        try {
            PasteMetadata metadata = metadataStore.get(shortLink);
            if (metadata == null) {
                return null;
            }
            
            if (metadata.getExpiresAtMs() != null && System.currentTimeMillis() > metadata.getExpiresAtMs()) {
                // Active TTL validation on read
                metadataStore.remove(shortLink);
                blobStore.remove(shortLink);
                return null;
            }
            
            return blobStore.get(shortLink);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int sweepExpiredPastes() {
        return ttlCleaner.sweep();
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