package v2_realistic;

/**
 * Demo for AsyncReplication
 */
public class Demo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Async Replication Demo ===\n");
        
        // Create system with 2 replicas, 500ms replication delay
        AsyncReplication db = new AsyncReplication(2, 500);
        
        // Write data
        System.out.println("--- Writing data ---");
        db.write("user:1", "Alice");
        
        // Immediate read - replica might not have data yet
        System.out.println("\n--- Immediate read (might miss) ---");
        db.readEventual("user:1");
        
        // Consistent read - falls back to primary
        System.out.println("\n--- Consistent read (falls back to primary) ---");
        db.readConsistent("user:1");
        
        // Wait for replication
        System.out.println("\n--- Waiting for replication (600ms) ---");
        Thread.sleep(600);
        
        // Now replica has data
        System.out.println("\n--- Read after replication ---");
        db.readEventual("user:1");
        db.readConsistent("user:1");
        
        // Multiple writes
        System.out.println("\n--- Multiple writes ---");
        db.write("user:2", "Bob");
        db.write("user:3", "Charlie");
        
        // Lag status
        db.printLagStatus();
        
        // Wait and check again
        Thread.sleep(600);
        db.printLagStatus();
        
        // Read from replicas
        System.out.println("\n--- Reading all users ---");
        db.readEventual("user:1");
        db.readEventual("user:2");
        db.readEventual("user:3");
        
        db.shutdown();
    }
}
