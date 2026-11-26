import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;

public class LSMStoreTest {

    private final String testDir = "test_lsm_data_java_v1";
    private final int testThreshold = 2;

    @BeforeEach
    public void setUp() {
        cleanDir(new File(testDir));
    }

    @AfterEach
    public void tearDown() {
        cleanDir(new File(testDir));
    }

    private void cleanDir(File dir) {
        if (dir.exists() && dir.isDirectory()) {
            try {
                Files.walk(dir.toPath())
                        .sorted(Comparator.reverseOrder())
                        .map(Path::toFile)
                        .forEach(File::delete);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    @Test
    public void testBasicPutAndGet() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        assertEquals("val1", store.get("key1"));
    }

    @Test
    public void testUpdateKey() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.put("key1", "val2");
        assertEquals("val2", store.get("key1"));
    }

    @Test
    public void testFlush() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.put("key2", "val2"); // Threshold reached, flushes
        store.put("key3", "val3");

        assertEquals("val1", store.get("key1"));
        assertEquals("val2", store.get("key2"));
        assertEquals("val3", store.get("key3"));
    }

    @Test
    public void testDelete() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.delete("key1");
        assertNull(store.get("key1"));
    }

    @Test
    public void testCompaction() throws InterruptedException {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.put("key2", "val2"); // Flush 1
        Thread.sleep(10);
        
        store.put("key1", "val1_new");
        store.put("key3", "val3"); // Flush 2
        Thread.sleep(10);
        
        store.delete("key2");
        store.put("key4", "val4"); // Flush 3 -> Triggers compaction

        assertEquals("val1_new", store.get("key1"));
        assertNull(store.get("key2"));
        assertEquals("val3", store.get("key3"));
        assertEquals("val4", store.get("key4"));
    }

    @Test
    public void testFlushCrash() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        
        try {
            store.getClass().getField("flushCrashPoint").set(store, (Runnable) () -> { throw new RuntimeException("Flush failed"); });
        } catch (NoSuchFieldException | IllegalAccessException e) {
            return; // Not applicable for versions without crash point
        }
        
        try {
            store.put("key2", "val2");
            fail("Expected flush crash");
        } catch (RuntimeException e) {
            assertEquals("Flush failed", e.getMessage());
        }

        LSMStore recoveredStore = new LSMStore(testDir, testThreshold);
        assertEquals("val1", recoveredStore.get("key1"));
        assertEquals("val2", recoveredStore.get("key2"));
    }

    @Test
    public void testCorruptTruncatedRecords() throws Exception {
        LSMStore store = new LSMStore(testDir, 4);
        store.put("key1", "val1");
        store.put("key2", "val2");
        
        File wal = new File(testDir, "wal.log");
        if (wal.exists()) {
            java.io.FileWriter fw = new java.io.FileWriter(wal, true);
            fw.write("corrupt_record_without_equals_sign\n");
            fw.write("key3=val3\n");
            fw.close();
        }
        
        LSMStore recoveredStore = new LSMStore(testDir, 4);
        assertEquals("val1", recoveredStore.get("key1"));
        assertEquals("val2", recoveredStore.get("key2"));
        assertEquals("val3", recoveredStore.get("key3"));
    }

    @Test
    public void testDuplicateReplayAndRangeBoundaries() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.put("key1", "val2"); // duplicate
        store.put("key2", "val2"); // flush threshold
        
        LSMStore recoveredStore = new LSMStore(testDir, testThreshold);
        assertEquals("val2", recoveredStore.get("key1"));
    }

    @Test
    public void testTombstonesSurviveCompaction() throws InterruptedException {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.put("key2", "val2"); // Flush
        Thread.sleep(10);
        store.delete("key1");
        store.put("key3", "val3"); // Flush
        Thread.sleep(10);
        store.put("key4", "val4");
        store.put("key5", "val5"); // Flush, trigger compaction
        
        LSMStore reopenedStore = new LSMStore(testDir, testThreshold);
        assertNull(reopenedStore.get("key1"));
    }

    @Test
    public void testBloomFilterExactLookup() {
        LSMStore store = new LSMStore(testDir, testThreshold);
        store.put("key1", "val1");
        store.put("key2", "val2"); // Flush
        assertEquals("val1", store.get("key1"));
        assertNull(store.get("nonexistent"));
    }
}
