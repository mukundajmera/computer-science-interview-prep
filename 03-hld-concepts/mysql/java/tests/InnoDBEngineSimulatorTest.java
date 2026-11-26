import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.Map;

class InnoDBEngineSimulatorTest {

    private InnoDBEngineSimulator simulator;

    @BeforeEach
    void setUp() {
        simulator = new InnoDBEngineSimulator();
    }

    @Test
    void testBufferPoolAndFlush() {
        // Set a small capacity for testing eviction
        simulator.bufferPool = new InnoDBEngineSimulator.BufferPool(2);

        int tx1 = simulator.startTransaction();

        Map<String, Object> data1 = new HashMap<>(); data1.put("val", 1);
        Map<String, Object> data2 = new HashMap<>(); data2.put("val", 2);
        Map<String, Object> data3 = new HashMap<>(); data3.put("val", 3);

        simulator.write(tx1, 1, data1);
        simulator.write(tx1, 2, data2);
        simulator.write(tx1, 3, data3); // Evicts 1

        assertFalse(simulator.bufferPool.pages.containsKey(1));
        assertTrue(simulator.bufferPool.pages.containsKey(2));
        assertTrue(simulator.bufferPool.pages.containsKey(3));

        simulator.flushDirtyPages();
        assertTrue(simulator.bufferPool.dirtyPages.isEmpty());
        assertTrue(simulator.diskStorage.containsKey(2));
        assertTrue(simulator.diskStorage.containsKey(3));
    }

    @Test
    void testMvccSnapshotIsolation() {
        int tx1 = simulator.startTransaction();
        Map<String, Object> data = new HashMap<>(); data.put("val", 100);
        simulator.write(tx1, 1, data);
        simulator.commit(tx1);

        int tx2 = simulator.startTransaction();
        assertEquals(100, simulator.read(tx2, 1).get("val"));

        int tx3 = simulator.startTransaction();
        Map<String, Object> dataNew = new HashMap<>(); dataNew.put("val", 200);
        simulator.write(tx3, 1, dataNew);

        assertEquals(100, simulator.read(tx2, 1).get("val")); // tx2 sees old version
        assertEquals(200, simulator.read(tx3, 1).get("val")); // tx3 sees own write

        simulator.commit(tx3);

        // tx2 should still see its snapshot
        assertEquals(100, simulator.read(tx2, 1).get("val"));
    }

    @Test
    void testRowLevelLocking() {
        int tx1 = simulator.startTransaction();
        Map<String, Object> data = new HashMap<>(); data.put("val", 1);
        simulator.write(tx1, 1, data);

        int tx2 = simulator.startTransaction();

        // Should timeout and throw Exception
        assertThrows(RuntimeException.class, () -> {
            Map<String, Object> data2 = new HashMap<>(); data2.put("val", 2);
            simulator.write(tx2, 1, data2);
        });

        simulator.commit(tx1);

        // Now it should succeed
        Map<String, Object> data3 = new HashMap<>(); data3.put("val", 3);
        assertTrue(simulator.write(tx2, 1, data3));
    }

    @Test
    void testRollback() {
        int tx1 = simulator.startTransaction();
        Map<String, Object> data = new HashMap<>(); data.put("val", 50);
        simulator.write(tx1, 1, data);
        simulator.commit(tx1);

        int tx2 = simulator.startTransaction();
        Map<String, Object> data2 = new HashMap<>(); data2.put("val", 99);
        simulator.write(tx2, 1, data2);

        simulator.rollback(tx2);

        int tx3 = simulator.startTransaction();
        assertEquals(50, simulator.read(tx3, 1).get("val"));
    }
}
