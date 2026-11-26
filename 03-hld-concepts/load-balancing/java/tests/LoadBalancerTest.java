package tests;

import v1_simple.*;
import v2_realistic.*;
import v3_production.*;

import java.util.*;

public class LoadBalancerTest {

    public static void main(String[] args) {
        System.out.println("Running LoadBalancerTest...");
        try {
            testRoundRobinEvenDistribution();
            testRoundRobinAddServer();
            testRoundRobinRemoveServer();

            testWeightedDistribution();
            testWeightedSkipUnhealthy();

            testConsistentHashStickySession();
            testConsistentHashMinimalRedistribution();
            testConsistentHashFailover();
            System.out.println("All tests passed!");
        } catch (AssertionError e) {
            System.err.println("Test failed: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }

    private static void assertNotEquals(Object notExpected, Object actual) {
        if (Objects.equals(notExpected, actual)) {
            throw new AssertionError("Did not expect " + notExpected + " but got it");
        }
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message != null ? message : "Expected condition to be true");
        }
    }
    
    private static void assertTrue(boolean condition) {
        assertTrue(condition, null);
    }

    private static void assertFalse(boolean condition) {
        if (condition) {
            throw new AssertionError("Expected condition to be false");
        }
    }

    private static void assertNotNull(Object obj) {
        if (obj == null) {
            throw new AssertionError("Expected object to not be null");
        }
    }

    static void testRoundRobinEvenDistribution() {
        RoundRobinLoadBalancer lb = new RoundRobinLoadBalancer(
            Arrays.asList("A", "B", "C")
        );

        Map<String, Integer> counts = new HashMap<>();
        for (int i = 0; i < 300; i++) {
            String server = lb.getNextServer();
            counts.merge(server, 1, Integer::sum);
        }

        assertEquals(100, counts.get("A"));
        assertEquals(100, counts.get("B"));
        assertEquals(100, counts.get("C"));
    }

    static void testRoundRobinAddServer() {
        RoundRobinLoadBalancer lb = new RoundRobinLoadBalancer(
            Arrays.asList("A", "B")
        );

        lb.addServer("C");

        assertEquals(3, lb.getServerCount());
        assertTrue(lb.getServers().contains("C"));
    }

    static void testRoundRobinRemoveServer() {
        RoundRobinLoadBalancer lb = new RoundRobinLoadBalancer(
            Arrays.asList("A", "B", "C")
        );

        lb.removeServer("B");

        assertEquals(2, lb.getServerCount());
        assertFalse(lb.getServers().contains("B"));
    }

    static void testWeightedDistribution() {
        List<WeightedLoadBalancer.Server> servers = Arrays.asList(
            new WeightedLoadBalancer.Server("A", 5),
            new WeightedLoadBalancer.Server("B", 3),
            new WeightedLoadBalancer.Server("C", 2)
        );
        WeightedLoadBalancer.HealthCheckConfig config =
            new WeightedLoadBalancer.HealthCheckConfig();
        WeightedLoadBalancer lb = new WeightedLoadBalancer(servers, config);
        try {
            Map<String, Integer> counts = new HashMap<>();
            for (int i = 0; i < 1000; i++) {
                String server = lb.getNextServer();
                counts.merge(server, 1, Integer::sum);
            }

            assertEquals(500, counts.get("A"));
            assertEquals(300, counts.get("B"));
            assertEquals(200, counts.get("C"));
        } finally {
            lb.shutdown();
        }
    }

    static void testWeightedSkipUnhealthy() {
        List<WeightedLoadBalancer.Server> servers = Arrays.asList(
            new WeightedLoadBalancer.Server("A", 1),
            new WeightedLoadBalancer.Server("B", 1),
            new WeightedLoadBalancer.Server("C", 1)
        );
        WeightedLoadBalancer.HealthCheckConfig config =
            new WeightedLoadBalancer.HealthCheckConfig();
        WeightedLoadBalancer lb = new WeightedLoadBalancer(servers, config);
        try {
            lb.markServerUnhealthy("B");

            for (int i = 0; i < 100; i++) {
                assertNotEquals("B", lb.getNextServer());
            }
            assertEquals(2, lb.getHealthyServerCount());
        } finally {
            lb.shutdown();
        }
    }

    static void testConsistentHashStickySession() {
        ConsistentHashingLB.HealthCheckConfig config =
            new ConsistentHashingLB.HealthCheckConfig();
        ConsistentHashingLB lb = new ConsistentHashingLB(100, config);
        try {
            lb.addServer("A", 1);
            lb.addServer("B", 1);
            lb.addServer("C", 1);

            String key = "user-123";
            String server1 = lb.getServerForKey(key);
            String server2 = lb.getServerForKey(key);
            String server3 = lb.getServerForKey(key);

            assertNotNull(server1);
            assertEquals(server1, server2);
            assertEquals(server2, server3);
        } finally {
            lb.shutdown();
        }
    }

    static void testConsistentHashMinimalRedistribution() {
        ConsistentHashingLB.HealthCheckConfig config =
            new ConsistentHashingLB.HealthCheckConfig();
        ConsistentHashingLB lb = new ConsistentHashingLB(100, config);
        try {
            lb.addServer("A", 1);
            lb.addServer("B", 1);
            lb.addServer("C", 1);

            Map<String, String> original = new HashMap<>();
            for (int i = 0; i < 1000; i++) {
                String key = "key-" + i;
                original.put(key, lb.getServerForKey(key));
            }

            lb.addServer("D", 1);

            int changed = 0;
            for (Map.Entry<String, String> entry : original.entrySet()) {
                if (!entry.getValue().equals(lb.getServerForKey(entry.getKey()))) {
                    changed++;
                }
            }

            assertTrue(changed > 0, "new server should receive some keys");
            assertTrue(changed < 500, "changed too many keys: " + changed);
        } finally {
            lb.shutdown();
        }
    }

    static void testConsistentHashFailover() {
        ConsistentHashingLB.HealthCheckConfig config =
            new ConsistentHashingLB.HealthCheckConfig();
        config.unhealthyThreshold = 1;
        ConsistentHashingLB lb = new ConsistentHashingLB(100, config);
        try {
            lb.addServer("A", 1);
            lb.addServer("B", 1);

            String keyForA = null;
            for (int i = 0; i < 5000; i++) {
                String key = "key-" + i;
                if ("A".equals(lb.getServerForKey(key))) {
                    keyForA = key;
                    break;
                }
            }
            assertNotNull(keyForA);

            lb.recordFailure("A");

            assertEquals("B", lb.getServerForKey(keyForA));
            assertEquals(1L, lb.getMetrics().getFailedRequests());
        } finally {
            lb.shutdown();
        }
    }
}
