/**
 * Demo for SimpleProxyCache
 */
public class SimpleDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Simple Proxy Cache Demo ===\n");
        
        // Create mock origin server
        SimpleProxyCache.OriginServer origin = url -> {
            // Simulate origin latency
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "Content for: " + url + " (fetched at " + System.currentTimeMillis() + ")";
        };
        
        // Create proxy cache with 5 second TTL
        SimpleProxyCache cache = new SimpleProxyCache(origin, 5000);
        
        // First request - cache miss
        System.out.println("Request 1:");
        String result1 = cache.fetch("/index.html");
        System.out.println("Result: " + result1);
        System.out.println();
        
        // Second request - cache hit
        System.out.println("Request 2 (same URL):");
        String result2 = cache.fetch("/index.html");
        System.out.println("Result: " + result2);
        System.out.println();
        
        // Different URL - cache miss
        System.out.println("Request 3 (different URL):");
        String result3 = cache.fetch("/about.html");
        System.out.println("Result: " + result3);
        System.out.println();
        
        // Multiple hits
        System.out.println("Multiple requests to cached URLs:");
        for (int i = 0; i < 5; i++) {
            cache.fetch("/index.html");
            cache.fetch("/about.html");
        }
        System.out.println();
        
        // Stats
        System.out.println("Cache Statistics:");
        System.out.println(cache.getStats());
        System.out.println();
        
        // Purge demonstration
        System.out.println("Purging /index.html:");
        cache.purge("/index.html");
        System.out.println();
        
        // After purge - cache miss
        System.out.println("Request after purge:");
        cache.fetch("/index.html");
        System.out.println();
        
        // Wait for TTL expiration
        System.out.println("Waiting for TTL expiration (5 seconds)...");
        Thread.sleep(5500);
        
        // After TTL - cache miss
        System.out.println("\nRequest after TTL expiration:");
        cache.fetch("/about.html");
        
        System.out.println("\nFinal Statistics:");
        System.out.println(cache.getStats());
    }
}
