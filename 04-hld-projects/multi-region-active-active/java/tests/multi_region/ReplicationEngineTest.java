package multi_region;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;

public class ReplicationEngineTest {

    @Test
    public void testBasicReplication() {
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

    @Test
    public void testConflictResolutionLWW() throws InterruptedException {
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

    @Test
    public void testConflictResolutionTieBreaker() {
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
}
