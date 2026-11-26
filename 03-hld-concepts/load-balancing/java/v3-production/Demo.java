package v3_production;

import java.util.*;

/**
 * Demo: Production Load Balancer with Consistent Hashing
 */
public class Demo {
    
    public static void main(String[] args) {
        System.out.println("=== Consistent Hashing Load Balancer Demo ===\n");
        
        // Demo 1: Consistent hashing for sticky sessions
        System.out.println("1. Consistent Hashing - Sticky Sessions:");
        demoConsistentHashing();
        
        // Demo 2: Minimal redistribution when adding/removing servers
        System.out.println("\n2. Minimal Redistribution on Server Change:");
        demoMinimalRedistribution();
        
        // Demo 3: Algorithm comparison
        System.out.println("\n3. Algorithm Comparison:");
        demoAlgorithms();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void demoConsistentHashing() {
        ConsistentHashingLB.HealthCheckConfig config = new ConsistentHashingLB.HealthCheckConfig();
        config.intervalMs = 60000; // Disable auto-checks for demo
        
        ConsistentHashingLB lb = new ConsistentHashingLB(100, config);
        lb.addServer("server-a", 1);
        lb.addServer("server-b", 1);
        lb.addServer("server-c", 1);
        
        // Same user ID should always go to same server
        String[] userIds = {"user-123", "user-456", "user-789"};
        
        System.out.println("   User ID → Server mapping (consistent):");
        for (String userId : userIds) {
            String server1 = lb.getServerForKey(userId);
            String server2 = lb.getServerForKey(userId);
            String server3 = lb.getServerForKey(userId);
            System.out.printf("   %s → %s (consistent: %s)%n", 
                userId, server1, 
                server1.equals(server2) && server2.equals(server3));
        }
        
        lb.shutdown();
    }
    
    private static void demoMinimalRedistribution() {
        ConsistentHashingLB.HealthCheckConfig config = new ConsistentHashingLB.HealthCheckConfig();
        config.intervalMs = 60000;
        
        ConsistentHashingLB lb = new ConsistentHashingLB(100, config);
        lb.addServer("server-a", 1);
        lb.addServer("server-b", 1);
        lb.addServer("server-c", 1);
        
        // Generate 1000 keys and track their server assignments
        Map<String, String> originalMapping = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String key = "key-" + i;
            originalMapping.put(key, lb.getServerForKey(key));
        }
        
        System.out.println("   Original: 3 servers, 1000 keys distributed");
        countDistribution(originalMapping);
        
        // Add a fourth server
        lb.addServer("server-d", 1);
        
        int changed = 0;
        for (Map.Entry<String, String> entry : originalMapping.entrySet()) {
            String newServer = lb.getServerForKey(entry.getKey());
            if (!newServer.equals(entry.getValue())) {
                changed++;
            }
        }
        
        System.out.printf("%n   After adding server-d: %d keys remapped (%.1f%%)%n", 
            changed, changed / 10.0);
        System.out.println("   Expected ~25% with consistent hashing (vs 75%+ with modulo)");
        
        lb.shutdown();
    }
    
    private static void countDistribution(Map<String, String> mapping) {
        Map<String, Integer> counts = new HashMap<>();
        for (String server : mapping.values()) {
            counts.merge(server, 1, Integer::sum);
        }
        counts.forEach((server, count) -> 
            System.out.printf("   %s: %d keys%n", server, count));
    }
    
    private static void demoAlgorithms() {
        ConsistentHashingLB.HealthCheckConfig config = new ConsistentHashingLB.HealthCheckConfig();
        config.intervalMs = 60000;
        
        ConsistentHashingLB lb = new ConsistentHashingLB(100, config);
        lb.addServer("server-a", 1);
        lb.addServer("server-b", 1);
        lb.addServer("server-c", 1);
        
        for (ConsistentHashingLB.Algorithm algo : ConsistentHashingLB.Algorithm.values()) {
            lb.setAlgorithm(algo);
            
            Map<String, Integer> distribution = new HashMap<>();
            for (int i = 0; i < 300; i++) {
                String server = lb.getServer();
                distribution.merge(server, 1, Integer::sum);
            }
            
            System.out.printf("   %s:%n", algo);
            distribution.forEach((server, count) -> 
                System.out.printf("      %s: %d%n", server, count));
        }
        
        lb.shutdown();
    }
}
