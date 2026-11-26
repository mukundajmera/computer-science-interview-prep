package v2_realistic;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Demo for range-based sharding.
 */
public class V2Demo {
    public static void main(String[] args) {
        System.out.println("=== Range-Based Sharding Demo ===\n");

        RangeShardRouter router = new RangeShardRouter();

        // Configure shards with ranges
        System.out.println("Configuring shards with ranges...");
        router.addShard("shard_1", 0, 1_000_000);
        router.addShard("shard_2", 1_000_000, 2_000_000);
        router.addShard("shard_3", 2_000_000, 3_000_000);
        router.addShard("shard_4", 3_000_000, 4_000_000);

        System.out.println("Shard 1: user_id 0 - 999,999");
        System.out.println("Shard 2: user_id 1,000,000 - 1,999,999");
        System.out.println("Shard 3: user_id 2,000,000 - 2,999,999");
        System.out.println("Shard 4: user_id 3,000,000 - 3,999,999\n");

        // Insert user data
        System.out.println("Inserting users...");
        long[] userIds = {100, 500_000, 1_500_000, 2_100_000, 3_500_000};
        
        for (long userId : userIds) {
            Map<String, Object> userData = new HashMap<>();
            userData.put("user_id", userId);
            userData.put("name", "User_" + userId);
            userData.put("email", "user" + userId + "@example.com");
            
            router.put(userId, userData);
            
            RangeShardRouter.ShardConfig config = router.routeToShard(userId);
            System.out.printf("User %d -> %s%n", userId, config.shardId);
        }

        System.out.println();
        router.printDistribution();

        // Demonstrate range query
        System.out.println("\n=== Range Query Demo ===");
        System.out.println("Querying users with ID 0 to 1,500,000:");
        List<Map<String, Object>> results = router.rangeQuery(0, 1_500_001);
        for (Map<String, Object> user : results) {
            System.out.println("  Found: " + user);
        }

        // Demonstrate point lookup
        System.out.println("\n=== Point Lookup ===");
        Map<String, Object> user = router.get(1_500_000);
        System.out.println("User 1,500,000: " + user);

        // Demonstrate shard failure handling
        System.out.println("\n=== Shard Failure Handling ===");
        System.out.println("Marking shard_2 as unhealthy...");
        router.markShardUnhealthy("shard_2");
        router.printDistribution();

        try {
            Map<String, Object> newUser = new HashMap<>();
            newUser.put("user_id", 1_600_000);
            router.put(1_600_000, newUser);
        } catch (RuntimeException e) {
            System.out.println("Error inserting to unhealthy shard: " + e.getMessage());
        }
    }
}
