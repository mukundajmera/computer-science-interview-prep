package v1_simple;

/**
 * Demo for simple hash-based sharding.
 */
public class V1Demo {
    public static void main(String[] args) {
        System.out.println("=== Hash-Based Sharding Demo ===\n");

        // Create router with 4 shards
        HashShardRouter router = new HashShardRouter(4);

        // Simulate storing user data
        System.out.println("Storing user data across shards...\n");
        
        String[] users = {
            "user_1001", "user_1002", "user_1003", "user_1004",
            "user_2001", "user_2002", "user_2003", "user_2004",
            "user_3001", "user_3002", "user_3003", "user_3004"
        };

        for (String userId : users) {
            String userData = "{\"name\": \"User " + userId + "\", \"email\": \"" + userId + "@example.com\"}";
            router.put(userId, userId, userData);
            int shardId = router.getShardId(userId);
            System.out.printf("User %s -> Shard %d%n", userId, shardId);
        }

        System.out.println();
        router.printDistribution();

        // Demonstrate retrieval
        System.out.println("\n=== Retrieving Data ===");
        String testUser = "user_1001";
        String retrieved = router.get(testUser, testUser);
        System.out.printf("Retrieved %s: %s%n", testUser, retrieved);

        // Demonstrate consistent hashing
        System.out.println("\n=== Consistency Check ===");
        System.out.println("Same key always goes to same shard:");
        for (int i = 0; i < 3; i++) {
            System.out.printf("user_1001 -> Shard %d%n", router.getShardId("user_1001"));
        }

        // Problem demonstration: hotspots
        System.out.println("\n=== Demonstrating Potential Hotspot ===");
        System.out.println("If shard key has low cardinality, distribution suffers:");
        HashShardRouter badRouter = new HashShardRouter(4);
        String[] statuses = {"active", "inactive", "pending"};
        for (int i = 0; i < 1000; i++) {
            String status = statuses[i % 3];
            badRouter.put(status, "item_" + i, "data");
        }
        badRouter.printDistribution();
    }
}
