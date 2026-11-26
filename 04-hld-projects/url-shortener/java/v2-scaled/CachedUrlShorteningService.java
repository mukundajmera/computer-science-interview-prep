/**
 * URL Shortener - V2 Scaled
 * 
 * Enhanced URL shortening service with caching layer.
 * Adds Redis caching and async analytics processing.
 */

import java.time.Instant;
import java.util.Optional;

/**
 * Cache interface for URL lookups.
 * Abstracts Redis or any other caching solution.
 */
interface UrlCache {
    /**
     * Get URL from cache.
     * @param shortCode The short code
     * @return The long URL if cached
     */
    Optional<String> get(String shortCode);
    
    /**
     * Put URL in cache with TTL.
     * @param shortCode The short code
     * @param longUrl The long URL
     * @param ttlSeconds Time to live in seconds
     */
    void put(String shortCode, String longUrl, int ttlSeconds);
    
    /**
     * Remove URL from cache.
     * @param shortCode The short code
     */
    void evict(String shortCode);
    
    /**
     * Check if key exists in cache.
     * @param shortCode The short code
     * @return true if exists
     */
    boolean exists(String shortCode);
}

/**
 * Message queue interface for async processing.
 */
interface MessageQueue {
    /**
     * Publish a click event for async processing.
     * @param event The click event
     */
    void publishClickEvent(ClickEvent event);
}

/**
 * Click event for analytics processing.
 */
class ClickEvent {
    private final String shortCode;
    private final Instant timestamp;
    private final String userAgent;
    private final String referrer;
    private final String ipHash;
    private final String country;
    
    public ClickEvent(String shortCode, String userAgent, String referrer, 
                      String ipHash, String country) {
        this.shortCode = shortCode;
        this.timestamp = Instant.now();
        this.userAgent = userAgent;
        this.referrer = referrer;
        this.ipHash = ipHash;
        this.country = country;
    }
    
    // Getters
    public String getShortCode() { return shortCode; }
    public Instant getTimestamp() { return timestamp; }
    public String getUserAgent() { return userAgent; }
    public String getReferrer() { return referrer; }
    public String getIpHash() { return ipHash; }
    public String getCountry() { return country; }
}

/**
 * Scaled URL shortening service with caching.
 * Wraps the basic service with cache-aside pattern.
 */
class CachedUrlShorteningService implements UrlShorteningService {
    
    private static final int DEFAULT_CACHE_TTL = 86400; // 24 hours
    
    private final UrlRepository repository;
    private final ShortCodeGenerator codeGenerator;
    private final UrlCache cache;
    private final MessageQueue messageQueue;
    private final String baseUrl;
    
    public CachedUrlShorteningService(UrlRepository repository,
                                      ShortCodeGenerator codeGenerator,
                                      UrlCache cache,
                                      MessageQueue messageQueue,
                                      String baseUrl) {
        this.repository = repository;
        this.codeGenerator = codeGenerator;
        this.cache = cache;
        this.messageQueue = messageQueue;
        this.baseUrl = baseUrl;
    }
    
    @Override
    public CreateUrlResponse createShortUrl(CreateUrlRequest request) {
        // Validate URL format
        validateUrl(request.getLongUrl());
        
        String shortCode;
        boolean isCustom = false;
        
        if (request.hasCustomAlias()) {
            String alias = request.getCustomAlias();
            
            if (!codeGenerator.isValidCustomAlias(alias)) {
                throw new IllegalArgumentException("Invalid custom alias format");
            }
            
            // Check cache first, then database
            if (cache.exists(alias) || repository.existsByShortCode(alias)) {
                throw new AliasAlreadyExistsException("Custom alias already exists: " + alias);
            }
            
            shortCode = alias;
            isCustom = true;
        } else {
            shortCode = codeGenerator.generate();
            
            int attempts = 0;
            while ((cache.exists(shortCode) || repository.existsByShortCode(shortCode)) 
                   && attempts < 5) {
                shortCode = codeGenerator.generate();
                attempts++;
            }
        }
        
        // Create and save entity
        UrlEntity entity = new UrlEntityBuilder()
            .shortCode(shortCode)
            .longUrl(request.getLongUrl())
            .expiresAt(request.getExpiresAt())
            .userId(request.getUserId())
            .custom(isCustom)
            .build();
        
        repository.save(entity);
        
        // Pre-populate cache (write-through)
        cache.put(shortCode, request.getLongUrl(), DEFAULT_CACHE_TTL);
        
        return new CreateUrlResponse(
            shortCode,
            baseUrl,
            request.getLongUrl(),
            entity.getCreatedAt(),
            request.getExpiresAt()
        );
    }
    
    @Override
    public Optional<String> getOriginalUrl(String shortCode) {
        // Try cache first (cache-aside pattern)
        Optional<String> cached = cache.get(shortCode);
        
        if (cached.isPresent()) {
            // Cache hit - publish analytics asynchronously
            publishClickEvent(shortCode);
            return cached;
        }
        
        // Cache miss - query database
        Optional<UrlEntity> entity = repository.findByShortCode(shortCode);
        
        if (entity.isEmpty()) {
            return Optional.empty();
        }
        
        UrlEntity url = entity.get();
        
        // Check expiration
        if (url.isExpired()) {
            // Evict from cache if expired
            cache.evict(shortCode);
            throw new UrlExpiredException("URL has expired: " + shortCode);
        }
        
        // Populate cache for future requests
        cache.put(shortCode, url.getLongUrl(), DEFAULT_CACHE_TTL);
        
        // Publish analytics asynchronously
        publishClickEvent(shortCode);
        
        return Optional.of(url.getLongUrl());
    }
    
    @Override
    public Optional<UrlStats> getStats(String shortCode) {
        return repository.findByShortCode(shortCode)
            .map(entity -> new UrlStats(
                entity.getShortCode(),
                entity.getLongUrl(),
                entity.getClickCount(),
                entity.getCreatedAt(),
                entity.getExpiresAt()
            ));
    }
    
    @Override
    public boolean deleteUrl(String shortCode) {
        boolean deleted = repository.deleteByShortCode(shortCode);
        
        if (deleted) {
            // Invalidate cache
            cache.evict(shortCode);
        }
        
        return deleted;
    }
    
    /**
     * Publish click event for async processing.
     */
    private void publishClickEvent(String shortCode) {
        // In production: Extract from request context
        ClickEvent event = new ClickEvent(shortCode, null, null, null, null);
        
        try {
            messageQueue.publishClickEvent(event);
        } catch (Exception e) {
            // Log but don't fail the redirect
            System.err.println("Failed to publish click event: " + e.getMessage());
        }
    }
    
    private void validateUrl(String urlString) {
        if (urlString == null || urlString.isEmpty()) {
            throw new IllegalArgumentException("URL cannot be empty");
        }
        
        try {
            java.net.URL url = new java.net.URL(urlString);
            String protocol = url.getProtocol().toLowerCase();
            
            if (!protocol.equals("http") && !protocol.equals("https")) {
                throw new IllegalArgumentException("Only HTTP/HTTPS URLs are allowed");
            }
        } catch (java.net.MalformedURLException e) {
            throw new IllegalArgumentException("Invalid URL format: " + urlString);
        }
    }
}

/**
 * In-memory cache implementation for testing.
 * In production: Use Redis client (Jedis, Lettuce).
 */
class InMemoryUrlCache implements UrlCache {
    
    private final java.util.Map<String, CacheEntry> store = 
        new java.util.concurrent.ConcurrentHashMap<>();
    
    static class CacheEntry {
        final String value;
        final long expiresAt;
        
        CacheEntry(String value, int ttlSeconds) {
            this.value = value;
            this.expiresAt = System.currentTimeMillis() + (ttlSeconds * 1000L);
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expiresAt;
        }
    }
    
    @Override
    public Optional<String> get(String shortCode) {
        CacheEntry entry = store.get(shortCode);
        
        if (entry == null || entry.isExpired()) {
            store.remove(shortCode);
            return Optional.empty();
        }
        
        return Optional.of(entry.value);
    }
    
    @Override
    public void put(String shortCode, String longUrl, int ttlSeconds) {
        store.put(shortCode, new CacheEntry(longUrl, ttlSeconds));
    }
    
    @Override
    public void evict(String shortCode) {
        store.remove(shortCode);
    }
    
    @Override
    public boolean exists(String shortCode) {
        CacheEntry entry = store.get(shortCode);
        return entry != null && !entry.isExpired();
    }
}

/**
 * In-memory message queue for testing.
 * In production: Use Kafka, RabbitMQ, or SQS.
 */
class InMemoryMessageQueue implements MessageQueue {
    
    private final java.util.Queue<ClickEvent> events = 
        new java.util.concurrent.ConcurrentLinkedQueue<>();
    
    @Override
    public void publishClickEvent(ClickEvent event) {
        events.offer(event);
    }
    
    /**
     * Get pending events (for testing/processing).
     */
    public java.util.List<ClickEvent> drain() {
        java.util.List<ClickEvent> result = new java.util.ArrayList<>();
        ClickEvent event;
        while ((event = events.poll()) != null) {
            result.add(event);
        }
        return result;
    }
}
