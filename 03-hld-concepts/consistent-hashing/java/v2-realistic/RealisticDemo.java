import java.util.*;

/**
 * Demo: Consistent Hash with Virtual Nodes
 */
public class RealisticDemo {
    
    public static void main(String[] args) {
        System.out.println("=== Virtual Node Consistent Hash Demo ===\n");
        
        // Demo 1: Better distribution with vnodes
        System.out.println("1. Distribution Comparison:");
        distributionDemo();
        
        // Demo 2: Weighted servers
        System.out.println("\n2. Weighted Servers:");
        weightedDemo();
        
        // Demo 3: Replication
        System.out.println("\n3. Replication:");
        replicationDemo();
        
        // Demo 4: Minimal redistribution
        System.out.println("\n4. Minimal Redistribution:");
        redistributionDemo();
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void distributionDemo() {
        // Compare distribution: 1 vnode vs 100 vnodes
        int[] vnodeCounts = {1, 10, 100};
        
        for (int vnodes : vnodeCounts) {
            VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(vnodes);
            ch.addServer("server-a");
            ch.addServer("server-b");
            ch.addServer("server-c");
            
            Map<String, Integer> dist = new HashMap<>();
            for (int i = 0; i < 10000; i++) {
                String server = ch.getServer("key-" + i);
                dist.merge(server, 1, Integer::sum);
            }
            
            System.out.printf("   %d vnodes per server:%n", vnodes);
            dist.forEach((s, c) -> 
                System.out.printf("      %s: %d (%.1f%%)%n", s, c, c / 100.0));
            
            // Calculate standard deviation
            double avg = 10000.0 / 3;
            double variance = dist.values().stream()
                .mapToDouble(c -> Math.pow(c - avg, 2))
                .average().orElse(0);
            System.out.printf("      Std Dev: %.1f%n", Math.sqrt(variance));
        }
    }
    
    private static void weightedDemo() {
        VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(50);
        
        // Server A has 2x capacity
        ch.addServer("server-a", 2);
        ch.addServer("server-b", 1);
        ch.addServer("server-c", 1);
        
        Map<String, Integer> dist = new HashMap<>();
        for (int i = 0; i < 10000; i++) {
            String server = ch.getServer("key-" + i);
            dist.merge(server, 1, Integer::sum);
        }
        
        System.out.println("   Weights: A=2, B=1, C=1");
        dist.forEach((s, c) -> 
            System.out.printf("      %s: %d (%.1f%%)%n", s, c, c / 100.0));
        System.out.println("   (A should get ~50%, B and C ~25% each)");
    }
    
    private static void replicationDemo() {
        VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(100);
        ch.addServer("server-a");
        ch.addServer("server-b");
        ch.addServer("server-c");
        ch.addServer("server-d");
        
        String key = "important:data:123";
        int replicationFactor = 3;
        
        List<String> replicas = ch.getServers(key, replicationFactor);
        
        System.out.printf("   Key: '%s'%n", key);
        System.out.printf("   Replication factor: %d%n", replicationFactor);
        System.out.printf("   Replica servers: %s%n", replicas);
    }
    
    private static void redistributionDemo() {
        VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(100);
        ch.addServer("server-a");
        ch.addServer("server-b");
        ch.addServer("server-c");
        
        // Store original mappings
        Map<String, String> original = new HashMap<>();
        for (int i = 0; i < 10000; i++) {
            String key = "key-" + i;
            original.put(key, ch.getServer(key));
        }
        
        // Add new server
        ch.addServer("server-d");
        
        // Count moved keys
        int moved = 0;
        for (int i = 0; i < 10000; i++) {
            String key = "key-" + i;
            if (!ch.getServer(key).equals(original.get(key))) {
                moved++;
            }
        }
        
        System.out.printf("   Original: 3 servers, 10000 keys%n");
        System.out.printf("   Added: server-d%n");
        System.out.printf("   Keys moved: %d (%.1f%%)%n", moved, moved / 100.0);
        System.out.printf("   Expected: ~25%% (1/4 of keys)%n");
    }
}
