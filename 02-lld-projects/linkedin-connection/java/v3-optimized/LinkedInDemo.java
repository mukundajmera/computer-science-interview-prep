package v3_optimized;

/**
 * LinkedIn Connection System - V1 Basic
 * 
 * Demo class showing usage of the connection system.
 */
public class LinkedInDemo {
    public static void main(String[] args) {
        System.out.println("=== LinkedIn Connection System Demo ===\n");
        
        NetworkService network = NetworkService.getInstance();
        
        // Register users
        System.out.println("--- Registering Users ---");
        User alice = new User("U001", "Alice Johnson", "alice@email.com", 
                             "Software Engineer at Tech Corp", "Tech Corp");
        User bob = new User("U002", "Bob Smith", "bob@email.com",
                           "Product Manager at StartupX", "StartupX");
        User charlie = new User("U003", "Charlie Brown", "charlie@email.com",
                               "Data Scientist at DataCo", "DataCo");
        User diana = new User("U004", "Diana Ross", "diana@email.com",
                             "Software Engineer at Tech Corp", "Tech Corp");
        
        network.registerUser(alice);
        network.registerUser(bob);
        network.registerUser(charlie);
        network.registerUser(diana);
        
        System.out.println("Registered " + network.getUserCount() + " users\n");
        
        // Send connection requests
        System.out.println("--- Sending Connection Requests ---");
        ConnectionRequest req1 = network.sendConnectionRequest("U001", "U002", 
            "Hi Bob, let's connect!");
        ConnectionRequest req2 = network.sendConnectionRequest("U001", "U003");
        ConnectionRequest req3 = network.sendConnectionRequest("U002", "U003");
        ConnectionRequest req4 = network.sendConnectionRequest("U001", "U004");
        
        // Accept some requests
        System.out.println("\n--- Processing Requests ---");
        network.acceptRequest(req1.getRequestId());
        network.acceptRequest(req2.getRequestId());
        network.acceptRequest(req3.getRequestId());
        network.acceptRequest(req4.getRequestId());
        
        // Display connections
        System.out.println("\n--- Connections ---");
        System.out.println("Alice's connections: " + 
                          network.getConnections("U001").size());
        System.out.println("Bob's connections: " + 
                          network.getConnections("U002").size());
        System.out.println("Charlie's connections: " + 
                          network.getConnections("U003").size());
        
        // Show mutual connections
        System.out.println("\n--- Mutual Connections ---");
        System.out.println("Mutual connections between Bob and Diana:");
        for (User mutual : network.getMutualConnections("U002", "U004")) {
            System.out.println("  - " + mutual.getName());
        }
        
        // Check if connected
        System.out.println("\n--- Connection Check ---");
        System.out.println("Alice connected to Bob? " + 
                          network.areConnected("U001", "U002"));
        System.out.println("Bob connected to Diana? " + 
                          network.areConnected("U002", "U004"));
        
        // Remove connection
        System.out.println("\n--- Removing Connection ---");
        network.removeConnection("U001", "U002");
        System.out.println("Removed connection between Alice and Bob");
        System.out.println("Alice connected to Bob now? " + 
                          network.areConnected("U001", "U002"));
        
        // Statistics
        System.out.println("\n--- Statistics ---");
        System.out.println("Total users: " + network.getUserCount());
        System.out.println("Total connections: " + network.getTotalConnectionCount());
        
        // Cleanup
        NetworkService.resetInstance();
        System.out.println("\n=== Demo Complete ===");
    }
}
