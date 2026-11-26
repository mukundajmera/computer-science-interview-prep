/**
 * Demo: Sliding Window Rate Limiter
 */
public class RealisticDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Sliding Window Rate Limiter Demo ===\n");
        
        // Demo 1: Basic per-user limiting
        System.out.println("1. Per-User Rate Limiting:");
        perUserDemo();
        
        // Demo 2: Multiple users
        System.out.println("\n2. Multiple Users:");
        multiUserDemo();
        
        // Demo 3: Window sliding
        System.out.println("\n3. Window Sliding Behavior:");
        windowSlidingDemo();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void perUserDemo() {
        // 5 requests per 10 seconds
        SlidingWindowRateLimiter limiter = new SlidingWindowRateLimiter(5, 10);
        
        String userId = "user-123";
        
        for (int i = 1; i <= 8; i++) {
            SlidingWindowRateLimiter.RateLimitResult result = limiter.tryAcquire(userId);
            System.out.printf("   Request %d: %s, remaining: %d%n",
                i, result.isAllowed() ? "ALLOWED" : "REJECTED", result.getRemaining());
        }
        
        System.out.println("   " + limiter.getStats());
    }
    
    private static void multiUserDemo() {
        // 3 requests per 10 seconds per user
        SlidingWindowRateLimiter limiter = new SlidingWindowRateLimiter(3, 10);
        
        String[] users = {"alice", "bob", "charlie"};
        
        for (String user : users) {
            for (int i = 1; i <= 5; i++) {
                SlidingWindowRateLimiter.RateLimitResult result = limiter.tryAcquire(user);
                System.out.printf("   %s request %d: %s%n",
                    user, i, result.isAllowed() ? "OK" : "BLOCKED");
            }
        }
        
        System.out.println("   " + limiter.getStats());
    }
    
    private static void windowSlidingDemo() throws InterruptedException {
        // 5 requests per 2 seconds
        SlidingWindowRateLimiter limiter = new SlidingWindowRateLimiter(5, 2);
        
        String userId = "user-456";
        
        // Use up all tokens
        System.out.println("   Initial burst:");
        for (int i = 1; i <= 5; i++) {
            SlidingWindowRateLimiter.RateLimitResult result = limiter.tryAcquire(userId);
            System.out.printf("   Request %d: %s%n", i, result.isAllowed() ? "OK" : "BLOCKED");
        }
        
        // Next request should be blocked
        SlidingWindowRateLimiter.RateLimitResult blocked = limiter.tryAcquire(userId);
        System.out.println("   Request 6: " + (blocked.isAllowed() ? "OK" : "BLOCKED"));
        
        // Wait 1 second (half window) - sliding window allows some requests
        System.out.println("\n   Waiting 1 second (half window)...");
        Thread.sleep(1000);
        
        SlidingWindowRateLimiter.RateLimitResult afterWait = limiter.tryAcquire(userId);
        System.out.println("   Request 7: " + (afterWait.isAllowed() ? "OK" : "BLOCKED") + 
            " (sliding window allows partial recovery)");
        
        // Wait another 1.5 seconds (total 2.5s - full window passed)
        System.out.println("\n   Waiting 1.5 more seconds...");
        Thread.sleep(1500);
        
        for (int i = 1; i <= 3; i++) {
            SlidingWindowRateLimiter.RateLimitResult result = limiter.tryAcquire(userId);
            System.out.printf("   Request: %s%n", result.isAllowed() ? "OK" : "BLOCKED");
        }
    }
}
