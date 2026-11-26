/**
 * Proxy Pattern - V3 Advanced: Caching Proxy
 * 
 * Demonstrates smart proxy with caching capabilities.
 */

import java.util.*;
import java.util.concurrent.*;

// Subject Interface
interface DataService {
    String fetchData(String key);
    void updateData(String key, String value);
}

// Real Subject - Simulates slow database
class DatabaseService implements DataService {
    private Map<String, String> database = new ConcurrentHashMap<>();
    
    public DatabaseService() {
        // Initialize with sample data
        database.put("user:1", "Alice");
        database.put("user:2", "Bob");
        database.put("product:1", "Laptop");
    }
    
    @Override
    public String fetchData(String key) {
        System.out.println("[DB] Fetching from database: " + key);
        simulateLatency();
        return database.get(key);
    }
    
    @Override
    public void updateData(String key, String value) {
        System.out.println("[DB] Updating database: " + key);
        simulateLatency();
        database.put(key, value);
    }
    
    private void simulateLatency() {
        try { Thread.sleep(500); } catch (Exception e) {}
    }
}

// Cache Entry with TTL
class CacheEntry {
    String value;
    long expireTime;
    
    CacheEntry(String value, long ttlMillis) {
        this.value = value;
        this.expireTime = System.currentTimeMillis() + ttlMillis;
    }
    
    boolean isExpired() {
        return System.currentTimeMillis() > expireTime;
    }
}

// Caching Proxy
class CachingDataServiceProxy implements DataService {
    private DataService realService;
    private Map<String, CacheEntry> cache = new ConcurrentHashMap<>();
    private long ttlMillis;
    private int hits = 0;
    private int misses = 0;
    
    public CachingDataServiceProxy(DataService realService, long ttlSeconds) {
        this.realService = realService;
        this.ttlMillis = ttlSeconds * 1000;
    }
    
    @Override
    public String fetchData(String key) {
        // Check cache first
        CacheEntry entry = cache.get(key);
        if (entry != null && !entry.isExpired()) {
            hits++;
            System.out.println("[CACHE] Hit for: " + key);
            return entry.value;
        }
        
        // Cache miss or expired
        misses++;
        System.out.println("[CACHE] Miss for: " + key);
        String value = realService.fetchData(key);
        
        if (value != null) {
            cache.put(key, new CacheEntry(value, ttlMillis));
        }
        
        return value;
    }
    
    @Override
    public void updateData(String key, String value) {
        // Write-through: update DB and invalidate cache
        realService.updateData(key, value);
        cache.remove(key);
        System.out.println("[CACHE] Invalidated: " + key);
    }
    
    // Smart proxy methods
    public void clearCache() {
        cache.clear();
        System.out.println("[CACHE] Cleared");
    }
    
    public double getHitRate() {
        int total = hits + misses;
        return total == 0 ? 0 : (double) hits / total * 100;
    }
    
    public String getStats() {
        return String.format("Hits: %d, Misses: %d, Rate: %.1f%%", 
            hits, misses, getHitRate());
    }
}

// Demo
public class CachingProxyDemo {
    public static void main(String[] args) {
        DataService dbService = new DatabaseService();
        CachingDataServiceProxy cachedService = 
            new CachingDataServiceProxy(dbService, 10);  // 10 second TTL
        
        System.out.println("=== First fetch (cache miss) ===");
        String user1 = cachedService.fetchData("user:1");
        System.out.println("Result: " + user1);
        
        System.out.println("\n=== Second fetch (cache hit) ===");
        user1 = cachedService.fetchData("user:1");
        System.out.println("Result: " + user1);
        
        System.out.println("\n=== Fetch different key (cache miss) ===");
        String user2 = cachedService.fetchData("user:2");
        System.out.println("Result: " + user2);
        
        System.out.println("\n=== Update invalidates cache ===");
        cachedService.updateData("user:1", "Alicia");
        
        System.out.println("\n=== Fetch after update (cache miss) ===");
        user1 = cachedService.fetchData("user:1");
        System.out.println("Result: " + user1);
        
        System.out.println("\n=== Cache Statistics ===");
        System.out.println(cachedService.getStats());
    }
}
