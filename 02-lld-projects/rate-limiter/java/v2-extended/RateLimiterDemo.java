/**
 * Rate Limiter - V1 Basic Demo
 * 
 * Demonstrates the Token Bucket rate limiter in action.
 */
public class RateLimiterDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Rate Limiter Demo (Token Bucket) ===\n");
        
        // Create rate limiter: 5 requests per second
        RateLimitConfig config = RateLimitConfig.perSecond(5);
        RateLimiter limiter = new RateLimiter(config);
        
        String clientId = "user123";
        
        // Test 1: Burst of requests
        System.out.println("Test 1: Sending 7 requests rapidly...");
        for (int i = 1; i <= 7; i++) {
            RateLimitResult result = limiter.allowRequest(clientId);
            System.out.printf("  Request %d: %s (remaining: %d)%n",
                    i, 
                    result.isAllowed() ? "ALLOWED" : "REJECTED",
                    result.getRemainingTokens());
        }
        
        // Test 2: Wait for token refill
        System.out.println("\nTest 2: Waiting 500ms for refill...");
        Thread.sleep(500);
        
        RateLimitResult result = limiter.allowRequest(clientId);
        System.out.printf("  Request after wait: %s (remaining: %d)%n",
                result.isAllowed() ? "ALLOWED" : "REJECTED",
                result.getRemainingTokens());
        
        // Test 3: Different client
        System.out.println("\nTest 3: Different client 'user456'...");
        String otherClient = "user456";
        for (int i = 1; i <= 3; i++) {
            result = limiter.allowRequest(otherClient);
            System.out.printf("  Request %d: %s (remaining: %d)%n",
                    i,
                    result.isAllowed() ? "ALLOWED" : "REJECTED",
                    result.getRemainingTokens());
        }
        
        // Test 4: Reset client
        System.out.println("\nTest 4: Resetting 'user123'...");
        limiter.resetClient(clientId);
        result = limiter.allowRequest(clientId);
        System.out.printf("  Request after reset: %s (remaining: %d)%n",
                result.isAllowed() ? "ALLOWED" : "REJECTED",
                result.getRemainingTokens());
        
        System.out.println("\n=== Demo Complete ===");
        System.out.println("Tracked clients: " + limiter.getClientCount());
    }
}
