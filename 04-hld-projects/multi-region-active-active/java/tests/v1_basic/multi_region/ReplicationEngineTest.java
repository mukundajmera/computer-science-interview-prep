package v1_basic.multi_region;

import java.util.Arrays;
import java.util.List;

/*
 * Simplifications in this simulator:
 * - Transport: In-memory method calls and local queues replace network communication, eliminating network partitions (unless simulated via boolean flags) and RPC overhead.
 * - Clock: Relies on the local machine's system time (System.currentTimeMillis()) for Hybrid Logical Clocks, assuming no drift across simulated regions.
 * - Security: Authentication, authorization, and data encryption are omitted for simplicity.
 * - Consistency: Immediate local updates are provided, but replication relies on explicit `.replicateTo()` calls to simulate eventual consistency across regions.
 */
public class ReplicationEngineTest {

    public static void main(String[] args) throws Exception {
        testBasicReplication();
        testConflictResolutionLWW();
        testConflictResolutionTieBreaker();
        testNetworkPartitionSplitBrain();
        System.out.println("All tests passed!");
    }

    private static void assertEquals(Object expected, Object actual) {
        if (expected == null && actual == null) return;
        if (expected != null && expected.equals(actual)) return;
        throw new AssertionError("Expected " + expected + " but got " + actual);
    }

    private static void assertNotNull(Object actual) {
        if (actual == null) {
            throw new AssertionError("Expected non-null but got null");
        }
    }

    private static void assertNull(Object actual) {
        if (actual != null) {
            throw new AssertionError("Expected null but got " + actual);
        }
    }

    public static void testBasicReplication() {
        RegionDatabase us = new RegionDatabase("US", Arrays.asList("EU", "APAC"));
        RegionDatabase eu = new RegionDatabase("EU", Arrays.asList("US", "APAC"));

        us.write("user1", "data-from-us");
        
        // Before replication, EU should not have it
        assertNull(eu.read("user1"));
        
        us.replicateTo(eu);
        
        // After replication, EU should have it
        assertNotNull(eu.read("user1"));
        assertEquals("data-from-us", eu.read("user1").getData());
    }

    public static void testConflictResolutionLWW() throws InterruptedException {
        RegionDatabase us = new RegionDatabase("US", Arrays.asList("EU"));
        RegionDatabase eu = new RegionDatabase("EU", Arrays.asList("US"));

        us.setPartitioned(true);
        eu.setPartitioned(true);

        us.write("user1", "data-from-us");
        Thread.sleep(10); // Ensure physical time advances for EU
        eu.write("user1", "data-from-eu");

        us.setPartitioned(false);
        eu.setPartitioned(false);

        us.replicateTo(eu);
        eu.replicateTo(us);

        // EU write was later, it should win
        assertEquals("data-from-eu", us.read("user1").getData());
        assertEquals("data-from-eu", eu.read("user1").getData());
    }

    public static void testConflictResolutionTieBreaker() {
        // Force a tie by mocking time or using identical timestamps
        RegionDatabase us = new RegionDatabase("US", Arrays.asList("EU"));
        RegionDatabase eu = new RegionDatabase("EU", Arrays.asList("US"));

        HybridLogicalClock clock = new HybridLogicalClock(1000, 0);
        
        Record recordUs = new Record("user1", "data-us", clock, "US", false);
        Record recordEu = new Record("user1", "data-eu", clock, "EU", false);
        
        us.applyReplication(recordUs);
        eu.applyReplication(recordEu);
        
        // Cross replicate
        us.applyReplication(recordEu);
        eu.applyReplication(recordUs);
        
        // US > EU lexically, so US wins the tiebreaker
        assertEquals("data-us", us.read("user1").getData());
        assertEquals("data-us", eu.read("user1").getData());
    }

    public static void testNetworkPartitionSplitBrain() throws InterruptedException {
        RegionDatabase us = new RegionDatabase("US", Arrays.asList("EU"));
        RegionDatabase eu = new RegionDatabase("EU", Arrays.asList("US"));
        
        // Simulate network partition (split-brain) as mentioned in DESIGN.md
        us.setPartitioned(true);
        eu.setPartitioned(true);

        us.write("shared-doc", "content-from-us");
        Thread.sleep(10);
        
        // Replication attempts during partition should not affect peers
        us.replicateTo(eu);
        assertNull(eu.read("shared-doc")); // EU should not see US writes yet

        eu.write("shared-doc", "content-from-eu-updated");

        // Heal partition
        us.setPartitioned(false);
        eu.setPartitioned(false);

        // Anti-entropy / background replication simulation
        us.replicateTo(eu);
        eu.replicateTo(us);

        // EU's write happened later, LWW with HLC resolves conflict
        assertEquals("content-from-eu-updated", us.read("shared-doc").getData());
        assertEquals("content-from-eu-updated", eu.read("shared-doc").getData());
    }
}
