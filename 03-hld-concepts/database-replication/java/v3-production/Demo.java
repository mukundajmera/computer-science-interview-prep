package v3_production;

/**
 * Demo for MultiPrimaryReplication
 */
public class Demo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Multi-Primary Replication Demo ===\n");
        
        // Create system with 3 primaries, 100ms replication delay
        MultiPrimaryReplication db = new MultiPrimaryReplication(3, 100);
        
        // Write to different primaries
        System.out.println("--- Writing to different primaries ---");
        db.write(0, "user:1", "Alice");
        db.write(1, "user:2", "Bob");
        db.write(2, "user:3", "Charlie");
        
        // Wait for replication
        Thread.sleep(300);
        
        // Read from any primary
        System.out.println("\n--- Reading from different primaries ---");
        db.read(0, "user:1");
        db.read(1, "user:1"); // Replicated from primary-0
        db.read(2, "user:2"); // Replicated from primary-1
        
        // Simulate conflict
        db.simulateConcurrentWrites("config", "value-from-dc1", "value-from-dc2");
        
        // Wait for conflict resolution
        Thread.sleep(300);
        
        // Check final values
        System.out.println("\n--- Final values after conflict resolution ---");
        db.read(0, "config");
        db.read(1, "config");
        db.read(2, "config");
        
        // Status
        db.printStatus();
        
        db.shutdown();
    }
}
