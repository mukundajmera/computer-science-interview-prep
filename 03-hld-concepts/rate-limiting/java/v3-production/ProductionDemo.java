import java.util.*;

/**
 * Demo: Production Distributed Rate Limiter
 */
public class ProductionDemo {
    
    public static void main(String[] args) {
        System.out.println("=== Production Rate Limiter Demo ===\n");
        
        // Create rate limiter with in-memory store
        DistributedRateLimiter.InMemoryRateLimitStore store = 
            new DistributedRateLimiter.InMemoryRateLimitStore();
        DistributedRateLimiter limiter = new DistributedRateLimiter(store);
        
        try {
            // Demo 1: Different tiers
            System.out.println("1. Tiered Rate Limiting:");
            tieredDemo(limiter);
            
            // Demo 2: HTTP headers
            System.out.println("\n2. HTTP Response Headers:");
            headersDemo(limiter);
            
            // Demo 3: Rate limiting simulation
            System.out.println("\n3. API Usage Simulation:");
            simulationDemo(limiter);
            
            // Demo 4: Metrics
            System.out.println("\n4. Metrics:");
            System.out.println("   " + limiter.getMetrics());
            
        } finally {
            limiter.shutdown();
        }
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void tieredDemo(DistributedRateLimiter limiter) {
        // Add custom tiers for demo (smaller limits)
        limiter.addTier(new DistributedRateLimiter.TierConfig("demo-free", 5, 60, 2));
        limiter.addTier(new DistributedRateLimiter.TierConfig("demo-premium", 20, 60, 5));
        
        System.out.println("   Free tier (5/min):");
        for (int i = 1; i <= 7; i++) {
            var result = limiter.checkRateLimit("free-user", "demo-free");
            System.out.printf("      Request %d: %s (remaining: %d)%n",
                i, result.isAllowed() ? "OK" : "BLOCKED", result.getRemaining());
        }
        
        System.out.println("\n   Premium tier (20/min):");
        for (int i = 1; i <= 7; i++) {
            var result = limiter.checkRateLimit("premium-user", "demo-premium");
            System.out.printf("      Request %d: %s (remaining: %d)%n",
                i, result.isAllowed() ? "OK" : "BLOCKED", result.getRemaining());
        }
    }
    
    private static void headersDemo(DistributedRateLimiter limiter) {
        limiter.addTier(new DistributedRateLimiter.TierConfig("header-demo", 3, 60, 1));
        
        // Make requests until blocked
        for (int i = 1; i <= 5; i++) {
            var result = limiter.checkRateLimit("header-user", "header-demo");
            Map<String, String> headers = result.getHeaders();
            
            System.out.printf("   Request %d - Status: %s%n", 
                i, result.isAllowed() ? "200 OK" : "429 Too Many Requests");
            headers.forEach((k, v) -> System.out.printf("      %s: %s%n", k, v));
            System.out.println();
        }
    }
    
    private static void simulationDemo(DistributedRateLimiter limiter) {
        // Simulate realistic API usage
        limiter.addTier(new DistributedRateLimiter.TierConfig("sim", 10, 60, 3));
        
        String[] users = {"user-A", "user-B", "user-C"};
        Random random = new Random(42);
        
        int total = 0;
        int allowed = 0;
        int rejected = 0;
        
        // Simulate 50 requests from random users
        for (int i = 0; i < 50; i++) {
            String user = users[random.nextInt(users.length)];
            var result = limiter.checkRateLimit(user, "sim");
            
            total++;
            if (result.isAllowed()) {
                allowed++;
            } else {
                rejected++;
            }
        }
        
        System.out.printf("   Simulated %d requests from 3 users%n", total);
        System.out.printf("   Allowed: %d, Rejected: %d%n", allowed, rejected);
        System.out.printf("   Acceptance rate: %.1f%%%n", (allowed * 100.0) / total);
    }
}
