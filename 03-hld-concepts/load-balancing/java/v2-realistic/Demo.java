package v2_realistic;

import java.util.*;

/**
 * Demo: Weighted Load Balancer with Health Checks
 */
public class Demo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Weighted Load Balancer Demo ===\n");
        
        // Demo 1: Weighted distribution
        System.out.println("1. Weighted Distribution:");
        demoWeightedDistribution();
        
        // Demo 2: Health checks
        System.out.println("\n2. Health Checks:");
        demoHealthChecks();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void demoWeightedDistribution() {
        // Create servers with different weights
        List<WeightedLoadBalancer.Server> servers = Arrays.asList(
            new WeightedLoadBalancer.Server("high-capacity-server", 5),   // 50% traffic
            new WeightedLoadBalancer.Server("medium-capacity-server", 3), // 30% traffic
            new WeightedLoadBalancer.Server("low-capacity-server", 2)     // 20% traffic
        );
        
        WeightedLoadBalancer.HealthCheckConfig config = new WeightedLoadBalancer.HealthCheckConfig();
        config.intervalSeconds = 1000; // Disable auto health checks for demo
        
        WeightedLoadBalancer lb = new WeightedLoadBalancer(servers, config);
        
        // Send 1000 requests and count distribution
        Map<String, Integer> counts = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String server = lb.getNextServer();
            counts.merge(server, 1, Integer::sum);
        }
        
        System.out.println("   Server weights: high=5, medium=3, low=2 (total=10)");
        System.out.println("   Distribution over 1000 requests:");
        counts.forEach((server, count) -> 
            System.out.printf("   %s: %d (%.1f%%)%n", 
                server, count, count / 10.0));
        
        lb.shutdown();
    }
    
    private static void demoHealthChecks() throws InterruptedException {
        // Track which servers are "healthy" in our simulation
        Set<String> simulatedHealthy = new HashSet<>();
        simulatedHealthy.add("server-1");
        simulatedHealthy.add("server-2");
        simulatedHealthy.add("server-3");
        
        List<WeightedLoadBalancer.Server> servers = Arrays.asList(
            new WeightedLoadBalancer.Server("server-1", 1),
            new WeightedLoadBalancer.Server("server-2", 1),
            new WeightedLoadBalancer.Server("server-3", 1)
        );
        
        WeightedLoadBalancer.HealthCheckConfig config = new WeightedLoadBalancer.HealthCheckConfig();
        config.intervalSeconds = 1;
        config.unhealthyThreshold = 2;
        config.checker = address -> simulatedHealthy.contains(address);
        
        WeightedLoadBalancer lb = new WeightedLoadBalancer(servers, config);
        
        System.out.println("   Initial: All 3 servers healthy");
        System.out.println("   Healthy count: " + lb.getHealthyServerCount());
        
        // Simulate server-2 failing
        System.out.println("\n   Simulating server-2 failure...");
        simulatedHealthy.remove("server-2");
        
        // Wait for health check to detect failure
        Thread.sleep(3000);
        
        System.out.println("   Healthy count after failure: " + lb.getHealthyServerCount());
        
        // Show which servers are getting traffic
        System.out.println("\n   Requests (server-2 should not receive any):");
        for (int i = 0; i < 6; i++) {
            System.out.println("   → " + lb.getNextServer());
        }
        
        // Simulate server-2 recovery
        System.out.println("\n   Simulating server-2 recovery...");
        simulatedHealthy.add("server-2");
        Thread.sleep(3000);
        
        System.out.println("   Healthy count after recovery: " + lb.getHealthyServerCount());
        
        lb.shutdown();
    }
}
