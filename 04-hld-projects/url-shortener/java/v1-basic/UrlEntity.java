/**
 * URL Shortener - V1 Basic
 * 
 * URL entity representing a shortened URL mapping.
 */

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Domain entity representing a shortened URL.
 */
class UrlEntity {
    private final String shortCode;
    private final String longUrl;
    private final Instant createdAt;
    private final Instant expiresAt;
    private final String userId;
    private final boolean isCustom;
    private long clickCount;
    private final Map<String, Object> metadata;
    
    public UrlEntity(String shortCode, String longUrl, Instant expiresAt, 
                     String userId, boolean isCustom) {
        this.shortCode = shortCode;
        this.longUrl = longUrl;
        this.createdAt = Instant.now();
        this.expiresAt = expiresAt;
        this.userId = userId;
        this.isCustom = isCustom;
        this.clickCount = 0;
        this.metadata = new HashMap<>();
    }
    
    /**
     * Check if this URL has expired.
     */
    public boolean isExpired() {
        return expiresAt != null && Instant.now().isAfter(expiresAt);
    }
    
    /**
     * Increment click count (for analytics).
     */
    public void incrementClickCount() {
        this.clickCount++;
    }
    
    // Getters
    public String getShortCode() { return shortCode; }
    public String getLongUrl() { return longUrl; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getExpiresAt() { return expiresAt; }
    public String getUserId() { return userId; }
    public boolean isCustom() { return isCustom; }
    public long getClickCount() { return clickCount; }
    public Map<String, Object> getMetadata() { return metadata; }
}

/**
 * Builder pattern for creating URL entities.
 */
class UrlEntityBuilder {
    private String shortCode;
    private String longUrl;
    private Instant expiresAt;
    private String userId;
    private boolean isCustom;
    
    public UrlEntityBuilder shortCode(String shortCode) {
        this.shortCode = shortCode;
        return this;
    }
    
    public UrlEntityBuilder longUrl(String longUrl) {
        this.longUrl = longUrl;
        return this;
    }
    
    public UrlEntityBuilder expiresAt(Instant expiresAt) {
        this.expiresAt = expiresAt;
        return this;
    }
    
    public UrlEntityBuilder userId(String userId) {
        this.userId = userId;
        return this;
    }
    
    public UrlEntityBuilder custom(boolean isCustom) {
        this.isCustom = isCustom;
        return this;
    }
    
    public UrlEntity build() {
        if (shortCode == null || longUrl == null) {
            throw new IllegalStateException("shortCode and longUrl are required");
        }
        return new UrlEntity(shortCode, longUrl, expiresAt, userId, isCustom);
    }
}
