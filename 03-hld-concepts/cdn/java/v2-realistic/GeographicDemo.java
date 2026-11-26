/**
 * Demo for GeographicCDN
 */
public class GeographicDemo {
    
    public static void main(String[] args) {
        System.out.println("=== Geographic CDN Demo ===\n");
        
        // Create origin server with latency simulation
        GeographicCDN.OriginServer origin = url -> {
            try {
                Thread.sleep(200); // Simulates origin latency
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "Content: " + url;
        };
        
        // Create CDN: shield TTL 60s, edge TTL 30s
        GeographicCDN cdn = new GeographicCDN(origin, 60000, 30000);
        
        // User from Japan requests content
        System.out.println("=== User from Japan ===");
        GeographicCDN.FetchResult result1 = cdn.fetch("japan", "/video/popular.mp4");
        System.out.println("Request 1: " + result1);
        
        // Same user requests again - edge cache hit
        GeographicCDN.FetchResult result2 = cdn.fetch("japan", "/video/popular.mp4");
        System.out.println("Request 2: " + result2);
        
        // User from Germany requests same content
        System.out.println("\n=== User from Germany ===");
        GeographicCDN.FetchResult result3 = cdn.fetch("germany", "/video/popular.mp4");
        System.out.println("Request 1: " + result3);
        System.out.println("(Shield already has content, no origin fetch)");
        
        // User from California
        System.out.println("\n=== User from California ===");
        GeographicCDN.FetchResult result4 = cdn.fetch("california", "/video/popular.mp4");
        System.out.println("Request 1: " + result4);
        
        // Multiple users from different regions
        System.out.println("\n=== Multiple Users, Same Content ===");
        String[] regions = {"japan", "germany", "california", "uk", "korea", "oregon"};
        for (String region : regions) {
            GeographicCDN.FetchResult result = cdn.fetch(region, "/video/popular.mp4");
            System.out.printf("User from %-12s -> Edge: %-10s Source: %s%n", 
                            region, result.servedBy, result.source);
        }
        
        // Different content from same region
        System.out.println("\n=== Different Content ===");
        GeographicCDN.FetchResult result5 = cdn.fetch("japan", "/images/logo.png");
        System.out.println("New content request: " + result5);
        
        // Global purge demonstration
        System.out.println("\n=== Global Purge ===");
        cdn.purgeGlobal("/video/popular.mp4");
        
        // After purge - all edges will need to refetch
        System.out.println("\nRequests after purge:");
        GeographicCDN.FetchResult result6 = cdn.fetch("japan", "/video/popular.mp4");
        System.out.println("Japan: " + result6);
        
        // Print statistics
        cdn.printStats();
    }
}
