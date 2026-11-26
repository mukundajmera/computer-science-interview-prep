import java.util.*;

/**
 * Demo: Simple Consistent Hash Ring
 */
public class SimpleDemo {
    
    public static void main(String[] args) {
        System.out.println("=== Simple Consistent Hash Demo ===\n");
        
        // Demo 1: Basic usage
        System.out.println("1. Basic Key-to-Server Mapping:");
        basicDemo();
        
        // Demo 2: Adding a server
        System.out.println("\n2. Adding a Server:");
        addServerDemo();
        
        // Demo 3: Consistency check
        System.out.println("\n3. Consistency Verification:");
        consistencyDemo();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void basicDemo() {
        SimpleConsistentHash ch = new SimpleConsistentHash();
        ch.addServer("server-a");
        ch.addServer("server-b");
        ch.addServer("server-c");
        
        String[] keys = {"user:1", "user:2", "user:3", "order:100", "product:xyz"};
        
        for (String key : keys) {
            String server = ch.getServer(key);
            System.out.printf("   %s → %s%n", key, server);
        }
    }
    
    private static void addServerDemo() {
        SimpleConsistentHash ch = new SimpleConsistentHash();
        ch.addServer("server-a");
        ch.addServer("server-b");
        ch.addServer("server-c");
        
        // Track original mappings
        Map<String, String> originalMappings = new HashMap<>();
        for (int i = 0; i < 100; i++) {
            String key = "key-" + i;
            originalMappings.put(key, ch.getServer(key));
        }
        
        // Count distribution
        Map<String, Integer> dist1 = countDistribution(originalMappings.values());
        System.out.println("   Before adding server:");
        dist1.forEach((s, c) -> System.out.printf("      %s: %d keys%n", s, c));
        
        // Add a new server
        ch.addServer("server-d");
        
        // Count how many keys moved
        int moved = 0;
        for (int i = 0; i < 100; i++) {
            String key = "key-" + i;
            String newServer = ch.getServer(key);
            if (!newServer.equals(originalMappings.get(key))) {
                moved++;
            }
        }
        
        Map<String, Integer> dist2 = new HashMap<>();
        for (int i = 0; i < 100; i++) {
            String server = ch.getServer("key-" + i);
            dist2.merge(server, 1, Integer::sum);
        }
        
        System.out.println("\n   After adding server-d:");
        dist2.forEach((s, c) -> System.out.printf("      %s: %d keys%n", s, c));
        System.out.printf("\n   Keys moved: %d (%.0f%%)%n", moved, moved * 1.0);
        System.out.println("   (Ideally ~25% with consistent hashing)");
    }
    
    private static void consistencyDemo() {
        SimpleConsistentHash ch = new SimpleConsistentHash();
        ch.addServer("server-a");
        ch.addServer("server-b");
        ch.addServer("server-c");
        
        String key = "user:12345";
        
        // Same key should always map to same server
        String server1 = ch.getServer(key);
        String server2 = ch.getServer(key);
        String server3 = ch.getServer(key);
        
        System.out.printf("   Key '%s' maps to:%n", key);
        System.out.printf("      Call 1: %s%n", server1);
        System.out.printf("      Call 2: %s%n", server2);
        System.out.printf("      Call 3: %s%n", server3);
        System.out.printf("   Consistent: %s%n", 
            server1.equals(server2) && server2.equals(server3));
    }
    
    private static Map<String, Integer> countDistribution(java.util.Collection<String> servers) {
        Map<String, Integer> dist = new HashMap<>();
        for (String s : servers) {
            dist.merge(s, 1, Integer::sum);
        }
        return dist;
    }
}
