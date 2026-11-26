/**
 * URL Shortener - V1 Basic
 * 
 * Repository interface for URL persistence.
 */

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for URL data access.
 * Implementations can use any database (SQL, NoSQL, in-memory).
 */
interface UrlRepository {
    /**
     * Save a URL entity to storage.
     * @param entity The URL entity to save
     */
    void save(UrlEntity entity);
    
    /**
     * Find a URL by its short code.
     * @param shortCode The short code to look up
     * @return The URL entity if found
     */
    Optional<UrlEntity> findByShortCode(String shortCode);
    
    /**
     * Find a URL by the original long URL.
     * @param longUrl The original URL
     * @return The URL entity if found
     */
    Optional<UrlEntity> findByLongUrl(String longUrl);
    
    /**
     * Delete a URL by its short code.
     * @param shortCode The short code to delete
     * @return true if deleted, false if not found
     */
    boolean deleteByShortCode(String shortCode);
    
    /**
     * Check if a short code already exists.
     * @param shortCode The short code to check
     * @return true if exists
     */
    boolean existsByShortCode(String shortCode);
    
    /**
     * Find all URLs for a user.
     * @param userId The user ID
     * @return List of URL entities
     */
    List<UrlEntity> findByUserId(String userId);
    
    /**
     * Increment click count for a URL.
     * @param shortCode The short code
     */
    void incrementClickCount(String shortCode);
}

/**
 * In-memory implementation for development/testing.
 * Production would use DynamoDB, Cassandra, or similar.
 */
class InMemoryUrlRepository implements UrlRepository {
    // Simulates database storage
    // In production: Replace with DynamoDB/Cassandra client
    private final java.util.Map<String, UrlEntity> urlStore = 
        new java.util.concurrent.ConcurrentHashMap<>();
    private final java.util.Map<String, String> longUrlIndex = 
        new java.util.concurrent.ConcurrentHashMap<>();
    
    @Override
    public void save(UrlEntity entity) {
        urlStore.put(entity.getShortCode(), entity);
        longUrlIndex.put(entity.getLongUrl(), entity.getShortCode());
    }
    
    @Override
    public Optional<UrlEntity> findByShortCode(String shortCode) {
        return Optional.ofNullable(urlStore.get(shortCode));
    }
    
    @Override
    public Optional<UrlEntity> findByLongUrl(String longUrl) {
        String shortCode = longUrlIndex.get(longUrl);
        if (shortCode == null) {
            return Optional.empty();
        }
        return findByShortCode(shortCode);
    }
    
    @Override
    public boolean deleteByShortCode(String shortCode) {
        UrlEntity removed = urlStore.remove(shortCode);
        if (removed != null) {
            longUrlIndex.remove(removed.getLongUrl());
            return true;
        }
        return false;
    }
    
    @Override
    public boolean existsByShortCode(String shortCode) {
        return urlStore.containsKey(shortCode);
    }
    
    @Override
    public java.util.List<UrlEntity> findByUserId(String userId) {
        java.util.List<UrlEntity> result = new java.util.ArrayList<>();
        for (UrlEntity entity : urlStore.values()) {
            if (userId.equals(entity.getUserId())) {
                result.add(entity);
            }
        }
        return result;
    }
    
    @Override
    public void incrementClickCount(String shortCode) {
        UrlEntity entity = urlStore.get(shortCode);
        if (entity != null) {
            entity.incrementClickCount();
        }
    }
}
