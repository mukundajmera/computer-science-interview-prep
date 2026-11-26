package v1_simple;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Demo: Round Robin Load Balancer
 * 
 * Demonstrates basic round-robin distribution of requests
 * across multiple servers.
 */
public class Demo {
    
    public static void main(String[] args) {
        System.out.println("=== Round Robin Load Balancer Demo ===\n");
        
        // Create load balancer with 3 servers
        RoundRobinLoadBalancer lb = new RoundRobinLoadBalancer(
            Arrays.asList("server-a:8080", "server-b:8080", "server-c:8080")
        );
        
        // Demo 1: Basic round robin
        System.out.println("1. Basic Round Robin Distribution:");
        for (int i = 1; i <= 9; i++) {
            String server = lb.getNextServer();
            System.out.printf("   Request %d → %s%n", i, server);
        }
        
        // Demo 2: Count distribution
        System.out.println("\n2. Distribution over 1000 requests:");
        lb = new RoundRobinLoadBalancer(
            Arrays.asList("server-a", "server-b", "server-c")
        );
        
        Map<String, Integer> distribution = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String server = lb.getNextServer();
            distribution.merge(server, 1, Integer::sum);
        }
        
        distribution.forEach((server, count) -> 
            System.out.printf("   %s: %d requests (%.1f%%)%n", 
                server, count, count / 10.0));
        
        // Demo 3: Adding/removing servers
        System.out.println("\n3. Dynamic Server Pool:");
        System.out.println("   Initial servers: " + lb.getServers());
        
        lb.addServer("server-d");
        System.out.println("   After adding server-d: " + lb.getServers());
        
        lb.removeServer("server-b");
        System.out.println("   After removing server-b: " + lb.getServers());
        
        System.out.println("\n   Next 4 requests:");
        for (int i = 1; i <= 4; i++) {
            System.out.printf("   Request %d → %s%n", i, lb.getNextServer());
        }
        
        // Demo 4: Simulating request handling
        System.out.println("\n4. Simulating Request Handling:");
        simulateRequests();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void simulateRequests() {
        RoundRobinLoadBalancer lb = new RoundRobinLoadBalancer(
            Arrays.asList(
                "api-server-1:8080",
                "api-server-2:8080",
                "api-server-3:8080"
            )
        );
        
        String[] endpoints = {"/users/123", "/products/456", "/orders/789"};
        
        for (String endpoint : endpoints) {
            String server = lb.getNextServer();
            String response = simulateRequest(server, endpoint);
            System.out.printf("   GET %s → %s: %s%n", endpoint, server, response);
        }
    }
    
    private static String simulateRequest(String server, String endpoint) {
        // Simulate network latency
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "200 OK";
    }
}
