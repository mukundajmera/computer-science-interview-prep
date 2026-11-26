package v1_simple;

/**
 * Demo for SimplePrimaryReplica
 */
public class Demo {
    
    public static void main(String[] args) {
        System.out.println("=== Simple Primary-Replica Demo ===\n");
        
        // Create system with 3 replicas
        SimplePrimaryReplica db = new SimplePrimaryReplica(3);
        
        // Write some data
        System.out.println("--- Writing data ---");
        db.write("user:1", "Alice");
        db.write("user:2", "Bob");
        db.write("user:3", "Charlie");
        
        System.out.println("\n--- Reading data from replicas ---");
        // Reads are distributed across replicas
        db.read("user:1");
        db.read("user:2");
        db.read("user:3");
        
        System.out.println("\n--- Reading from primary (consistency) ---");
        db.readFromPrimary("user:1");
        
        System.out.println("\n--- Update and read ---");
        db.write("user:1", "Alice Updated");
        db.read("user:1");
        
        db.printStatus();
    }
}
