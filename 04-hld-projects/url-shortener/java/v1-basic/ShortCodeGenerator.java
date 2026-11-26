/**
 * URL Shortener - V1 Basic
 * 
 * Short code generation service.
 * This basic version uses a simple counter with base62 encoding.
 */

import java.util.concurrent.atomic.AtomicLong;

/**
 * Interface for generating unique short codes.
 */
interface ShortCodeGenerator {
    /**
     * Generate a new unique short code.
     * @return A unique short code string
     */
    String generate();
    
    /**
     * Validate if a custom alias is acceptable.
     * @param alias The custom alias to validate
     * @return true if valid
     */
    boolean isValidCustomAlias(String alias);
}

/**
 * Counter-based short code generator using Base62 encoding.
 * Simple but has scalability limitations (single counter).
 * 
 * In production: Use distributed Key Generation Service (KGS)
 */
class CounterBasedGenerator implements ShortCodeGenerator {
    
    // Base62 characters: a-z, A-Z, 0-9
    private static final String BASE62_CHARS = 
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    
    private static final int CODE_LENGTH = 7;
    private static final int BASE = 62;
    
    // Atomic counter for thread safety
    // In production: This would be a distributed counter or pre-generated pool
    private final AtomicLong counter;
    
    public CounterBasedGenerator() {
        // Start from a large number to get 7-char codes immediately
        this.counter = new AtomicLong(100_000_000L);
    }
    
    public CounterBasedGenerator(long startValue) {
        this.counter = new AtomicLong(startValue);
    }
    
    @Override
    public String generate() {
        long id = counter.incrementAndGet();
        return encodeBase62(id);
    }
    
    /**
     * Encode a number to base62 string.
     */
    private String encodeBase62(long number) {
        StringBuilder sb = new StringBuilder();
        
        while (number > 0) {
            int remainder = (int) (number % BASE);
            sb.insert(0, BASE62_CHARS.charAt(remainder));
            number /= BASE;
        }
        
        // Pad to minimum length if needed
        while (sb.length() < CODE_LENGTH) {
            sb.insert(0, 'a');
        }
        
        return sb.toString();
    }
    
    /**
     * Decode a base62 string back to number.
     */
    public long decodeBase62(String code) {
        long result = 0;
        for (char c : code.toCharArray()) {
            result = result * BASE + BASE62_CHARS.indexOf(c);
        }
        return result;
    }
    
    @Override
    public boolean isValidCustomAlias(String alias) {
        if (alias == null || alias.isEmpty()) {
            return false;
        }
        
        // Check length (3-20 characters)
        if (alias.length() < 3 || alias.length() > 20) {
            return false;
        }
        
        // Check for valid characters (alphanumeric and hyphens)
        for (char c : alias.toCharArray()) {
            if (!Character.isLetterOrDigit(c) && c != '-' && c != '_') {
                return false;
            }
        }
        
        // No leading/trailing hyphens
        if (alias.startsWith("-") || alias.endsWith("-")) {
            return false;
        }
        
        return true;
    }
}
