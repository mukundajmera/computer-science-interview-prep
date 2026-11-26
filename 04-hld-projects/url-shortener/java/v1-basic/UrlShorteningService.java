/**
 * URL Shortener Service - V1 Basic
 * 
 * Core URL shortening service implementation.
 * This version provides basic functionality without caching or scaling.
 */

import java.time.Instant;
import java.util.Optional;

/**
 * Main service interface for URL shortening operations.
 */
interface UrlShorteningService {
    /**
     * Creates a short URL for the given long URL.
     * @param request The URL creation request
     * @return The created short URL response
     */
    CreateUrlResponse createShortUrl(CreateUrlRequest request);
    
    /**
     * Retrieves the original URL for a given short code.
     * @param shortCode The short code to look up
     * @return The original URL if found
     */
    Optional<String> getOriginalUrl(String shortCode);
    
    /**
     * Gets analytics for a short URL.
     * @param shortCode The short code
     * @return URL statistics
     */
    Optional<UrlStats> getStats(String shortCode);
    
    /**
     * Deletes a short URL.
     * @param shortCode The short code to delete
     * @return true if deleted, false if not found
     */
    boolean deleteUrl(String shortCode);
}

/**
 * Request DTO for creating a short URL.
 */
class CreateUrlRequest {
    private final String longUrl;
    private final String customAlias;     // Optional
    private final Instant expiresAt;      // Optional
    private final String userId;          // Optional
    
    public CreateUrlRequest(String longUrl) {
        this(longUrl, null, null, null);
    }
    
    public CreateUrlRequest(String longUrl, String customAlias, Instant expiresAt, String userId) {
        this.longUrl = longUrl;
        this.customAlias = customAlias;
        this.expiresAt = expiresAt;
        this.userId = userId;
    }
    
    public String getLongUrl() { return longUrl; }
    public String getCustomAlias() { return customAlias; }
    public Instant getExpiresAt() { return expiresAt; }
    public String getUserId() { return userId; }
    public boolean hasCustomAlias() { return customAlias != null && !customAlias.isEmpty(); }
}

/**
 * Response DTO for short URL creation.
 */
class CreateUrlResponse {
    private final String shortCode;
    private final String shortUrl;
    private final String longUrl;
    private final Instant createdAt;
    private final Instant expiresAt;
    
    public CreateUrlResponse(String shortCode, String baseUrl, String longUrl, 
                            Instant createdAt, Instant expiresAt) {
        this.shortCode = shortCode;
        this.shortUrl = baseUrl + "/" + shortCode;
        this.longUrl = longUrl;
        this.createdAt = createdAt;
        this.expiresAt = expiresAt;
    }
    
    public String getShortCode() { return shortCode; }
    public String getShortUrl() { return shortUrl; }
    public String getLongUrl() { return longUrl; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getExpiresAt() { return expiresAt; }
}

/**
 * URL statistics DTO.
 */
class UrlStats {
    private final String shortCode;
    private final String longUrl;
    private final long clickCount;
    private final Instant createdAt;
    private final Instant expiresAt;
    
    public UrlStats(String shortCode, String longUrl, long clickCount,
                   Instant createdAt, Instant expiresAt) {
        this.shortCode = shortCode;
        this.longUrl = longUrl;
        this.clickCount = clickCount;
        this.createdAt = createdAt;
        this.expiresAt = expiresAt;
    }
    
    public String getShortCode() { return shortCode; }
    public String getLongUrl() { return longUrl; }
    public long getClickCount() { return clickCount; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getExpiresAt() { return expiresAt; }
}
