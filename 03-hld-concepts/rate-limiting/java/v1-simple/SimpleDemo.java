/**
 * Demo: Token Bucket Rate Limiter
 */
public class SimpleDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Token Bucket Rate Limiter Demo ===\n");
        
        // Demo 1: Basic usage
        System.out.println("1. Basic Usage (10 tokens, 2 per second refill):");
        basicUsageDemo();
        
        // Demo 2: Burst handling
        System.out.println("\n2. Burst Handling:");
        burstDemo();
        
        // Demo 3: Sustained rate
        System.out.println("\n3. Sustained Rate:");
        sustainedRateDemo();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void basicUsageDemo() throws InterruptedException {
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(10, 2);
        
        // Make 15 requests quickly
        for (int i = 1; i <= 15; i++) {
            boolean allowed = limiter.tryAcquire();
            System.out.printf("   Request %d: %s (tokens: %.1f)%n",
                i, allowed ? "ALLOWED" : "REJECTED", limiter.getAvailableTokens());
        }
        
        // Wait for refill
        System.out.println("   Waiting 2 seconds...");
        Thread.sleep(2000);
        
        boolean allowed = limiter.tryAcquire();
        System.out.printf("   After wait: %s (tokens: %.1f)%n",
            allowed ? "ALLOWED" : "REJECTED", limiter.getAvailableTokens());
    }
    
    private static void burstDemo() {
        // High capacity allows bursts
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(100, 10);
        
        // Simulate burst of 50 requests
        int allowed = 0;
        for (int i = 0; i < 50; i++) {
            if (limiter.tryAcquire()) {
                allowed++;
            }
        }
        
        System.out.printf("   Burst of 50 requests: %d allowed%n", allowed);
        System.out.printf("   Remaining tokens: %.1f%n", limiter.getAvailableTokens());
    }
    
    private static void sustainedRateDemo() throws InterruptedException {
        // 5 requests per second sustained
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(5, 5);
        
        int totalAllowed = 0;
        int totalRejected = 0;
        
        long startTime = System.currentTimeMillis();
        
        // Try 50 requests over 5 seconds (10 per second attempted)
        for (int second = 0; second < 5; second++) {
            for (int req = 0; req < 10; req++) {
                if (limiter.tryAcquire()) {
                    totalAllowed++;
                } else {
                    totalRejected++;
                }
            }
            Thread.sleep(1000);
        }
        
        long elapsed = System.currentTimeMillis() - startTime;
        
        System.out.printf("   Duration: %.1f seconds%n", elapsed / 1000.0);
        System.out.printf("   Total allowed: %d (expected ~25)%n", totalAllowed);
        System.out.printf("   Total rejected: %d%n", totalRejected);
        System.out.printf("   Effective rate: %.1f req/sec%n",
            totalAllowed / (elapsed / 1000.0));
    }
}
