package tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import v1_simple.SimplePrimaryReplica;

public class SimplePrimaryReplicaTest {

    private SimplePrimaryReplica db;

    @BeforeEach
    public void setUp() {
        // Initialize with 3 replicas for testing
        db = new SimplePrimaryReplica(3);
    }

    @Test
    public void testWriteAndReadFromReplica() {
        // Write data to the primary
        db.write("key1", "value1");

        // The write should be synchronously replicated to replicas
        // Read should return the written value (from a replica)
        String value = db.read("key1");
        assertEquals("value1", value, "Read from replica should return the written value");
    }

    @Test
    public void testReadFromPrimaryConsistency() {
        db.write("key2", "value2");

        // Reading directly from primary should return the value immediately
        String value = db.readFromPrimary("key2");
        assertEquals("value2", value, "Read from primary should return the written value");
    }

    @Test
    public void testZeroReplicasFallback() {
        SimplePrimaryReplica zeroReplicaDb = new SimplePrimaryReplica(0);
        zeroReplicaDb.write("key3", "value3");

        // When there are no replicas, read() should fallback to primary
        String value = zeroReplicaDb.read("key3");
        assertEquals("value3", value, "Should read from primary if no replicas are available");
    }
}
