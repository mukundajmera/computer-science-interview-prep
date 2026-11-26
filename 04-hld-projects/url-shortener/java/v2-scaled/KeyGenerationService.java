/**
 * URL Shortener - V2 Scaled
 * 
 * Key Generation Service (KGS) for distributed unique ID generation.
 * Pre-generates keys to avoid runtime collision detection.
 */

import java.util.Queue;
import java.util.Set;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Key Generation Service for pre-generating unique short codes.
 * Eliminates collision detection at runtime by using pre-generated pool.
 */
class KeyGenerationService implements ShortCodeGenerator {
    
    private static final int BATCH_SIZE = 1000;
    private static final int REFILL_THRESHOLD = 100;
    private static final String BASE62_CHARS = 
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    
    private final KeyRepository keyRepository;
    private final Queue<String> localKeyPool;
    private final AtomicInteger poolSize;
    
    public KeyGenerationService(KeyRepository keyRepository) {
        this.keyRepository = keyRepository;
        this.localKeyPool = new ConcurrentLinkedQueue<>();
        this.poolSize = new AtomicInteger(0);
        
        // Initial fill
        refillLocalPool();
    }
    
    @Override
    public String generate() {
        // Check if need to refill
        if (poolSize.get() < REFILL_THRESHOLD) {
            refillLocalPoolAsync();
        }
        
        String key = localKeyPool.poll();
        
        if (key == null) {
            // Pool exhausted, synchronous refill
            refillLocalPool();
            key = localKeyPool.poll();
        }
        
        if (key != null) {
            poolSize.decrementAndGet();
            // Mark as used in repository
            keyRepository.markAsUsed(key);
        }
        
        return key;
    }
    
    @Override
    public boolean isValidCustomAlias(String alias) {
        if (alias == null || alias.isEmpty()) {
            return false;
        }
        
        if (alias.length() < 3 || alias.length() > 20) {
            return false;
        }
        
        for (char c : alias.toCharArray()) {
            if (!Character.isLetterOrDigit(c) && c != '-' && c != '_') {
                return false;
            }
        }
        
        return !alias.startsWith("-") && !alias.endsWith("-");
    }
    
    /**
     * Refill local pool from repository.
     */
    private synchronized void refillLocalPool() {
        java.util.List<String> batch = keyRepository.getUnusedKeys(BATCH_SIZE);
        
        for (String key : batch) {
            localKeyPool.offer(key);
            poolSize.incrementAndGet();
        }
    }
    
    /**
     * Async refill (would use executor in production).
     */
    private void refillLocalPoolAsync() {
        // In production: Use ExecutorService
        // For simplicity, doing synchronous here
        refillLocalPool();
    }
    
    /**
     * Get current pool size.
     */
    public int getPoolSize() {
        return poolSize.get();
    }
}

/**
 * Repository for key pool management.
 */
interface KeyRepository {
    /**
     * Get batch of unused keys.
     * @param count Number of keys to retrieve
     * @return List of unused short codes
     */
    java.util.List<String> getUnusedKeys(int count);
    
    /**
     * Mark a key as used.
     * @param shortCode The short code
     */
    void markAsUsed(String shortCode);
    
    /**
     * Add new keys to the pool.
     * @param keys The keys to add
     */
    void addKeys(java.util.List<String> keys);
    
    /**
     * Get count of unused keys.
     * @return Number of available keys
     */
    int getUnusedKeyCount();
}

/**
 * In-memory key repository for testing.
 * In production: Use database table with used/unused status.
 */
class InMemoryKeyRepository implements KeyRepository {
    
    private static final String BASE62_CHARS = 
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    
    private final Queue<String> unusedKeys = new ConcurrentLinkedQueue<>();
    private final Set<String> usedKeys = java.util.concurrent.ConcurrentHashMap.newKeySet();
    
    public InMemoryKeyRepository() {
        // Pre-populate with some keys
        generateInitialKeys(10000);
    }
    
    private void generateInitialKeys(int count) {
        java.util.Random random = new java.util.Random();
        
        for (int i = 0; i < count; i++) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < 7; j++) {
                sb.append(BASE62_CHARS.charAt(random.nextInt(62)));
            }
            String key = sb.toString();
            
            if (!usedKeys.contains(key) && !unusedKeys.contains(key)) {
                unusedKeys.offer(key);
            }
        }
    }
    
    @Override
    public java.util.List<String> getUnusedKeys(int count) {
        java.util.List<String> result = new java.util.ArrayList<>();
        
        for (int i = 0; i < count; i++) {
            String key = unusedKeys.poll();
            if (key == null) {
                // Generate more if pool is empty
                generateInitialKeys(count * 2);
                key = unusedKeys.poll();
            }
            if (key != null) {
                result.add(key);
            }
        }
        
        return result;
    }
    
    @Override
    public void markAsUsed(String shortCode) {
        usedKeys.add(shortCode);
    }
    
    @Override
    public void addKeys(java.util.List<String> keys) {
        for (String key : keys) {
            if (!usedKeys.contains(key)) {
                unusedKeys.offer(key);
            }
        }
    }
    
    @Override
    public int getUnusedKeyCount() {
        return unusedKeys.size();
    }
}
