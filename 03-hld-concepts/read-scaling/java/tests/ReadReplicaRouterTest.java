package v1_simple;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

public class ReadReplicaRouterTest {

    private ReadReplicaRouter router;

    @BeforeEach
    public void setUp() {
        router = new ReadReplicaRouter("primary-db", Arrays.asList("replica-1", "replica-2"), 5000);
    }

    @Test
    public void testWritesAlwaysGoToPrimary() {
        assertEquals("primary-db", router.routeWrite("user1"));
        assertEquals("primary-db", router.routeWrite("user2"));
    }

    @Test
    public void testReadsLoadBalanceAcrossHealthyReplicas() {
        Set<String> routed = new HashSet<>();
        for (int i = 0; i < 10; i++) {
            routed.add(router.routeRead("user-read-only"));
        }
        assertTrue(routed.contains("replica-1"));
        assertTrue(routed.contains("replica-2"));
        assertFalse(routed.contains("primary-db"));
    }

    @Test
    public void testEvictionOnUnhealthyReplica() {
        router.updateReplicaHealth("replica-1", false);
        Set<String> routed = new HashSet<>();
        for (int i = 0; i < 10; i++) {
            routed.add(router.routeRead("user-read-only"));
        }
        assertTrue(routed.contains("replica-2"));
        assertFalse(routed.contains("replica-1"));
        assertFalse(routed.contains("primary-db"));

        // If all replicas unhealthy, fallback to primary
        router.updateReplicaHealth("replica-2", false);
        assertEquals("primary-db", router.routeRead("user-read-only"));
    }

    @Test
    public void testEvictionOnHighLag() {
        router.updateReplicaLag("replica-1", 6000); // Exceeds maxLagMs of 5000
        Set<String> routed = new HashSet<>();
        for (int i = 0; i < 10; i++) {
            routed.add(router.routeRead("user-read-only"));
        }
        assertTrue(routed.contains("replica-2"));
        assertFalse(routed.contains("replica-1"));

        // Exceed on both, fallback to primary
        router.updateReplicaLag("replica-2", 7000);
        assertEquals("primary-db", router.routeRead("user-read-only"));
    }

    @Test
    public void testReadYourOwnWrites() {
        router.setMockTime(1000);
        router.routeWrite("user1"); // user1 writes at t=1000

        router.setMockTime(1500); // Time elapsed = 500ms

        // replica-1 lag is 600ms (> elapsed 500ms). It's too stale for user1!
        router.updateReplicaLag("replica-1", 600);
        // replica-2 lag is 200ms (< elapsed 500ms). It's fresh enough for user1!
        router.updateReplicaLag("replica-2", 200);

        // routeRead for user1 should strictly route to replica-2
        Set<String> routed = new HashSet<>();
        for (int i = 0; i < 10; i++) {
            routed.add(router.routeRead("user1"));
        }
        assertTrue(routed.contains("replica-2"));
        assertFalse(routed.contains("replica-1"));
        assertFalse(routed.contains("primary-db"));

        // user2 hasn't written, can read from both
        Set<String> routedUser2 = new HashSet<>();
        for (int i = 0; i < 10; i++) {
            routedUser2.add(router.routeRead("user2"));
        }
        assertTrue(routedUser2.contains("replica-1"));
        assertTrue(routedUser2.contains("replica-2"));
    }
}
