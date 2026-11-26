import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;

public class KeyValueStoreLsmAll_versionsTest {

    private String testDir = "test_kvlsm_data";

    @BeforeEach
    public void setUp() {
        cleanDir(new File(testDir));
    }

    @AfterEach
    public void tearDown() {
        cleanDir(new File(testDir));
    }

    private void cleanDir(File dir) {
        if (dir.exists()) {
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
        KeyValueStoreLsm store = new KeyValueStoreLsm(testDir, 2);
        store.put("key1", "val1");
        assertEquals("val1", store.get("key1"));
    }

    @Test
    public void testUpdateKey() {
        KeyValueStoreLsm store = new KeyValueStoreLsm(testDir, 2);
        store.put("key1", "val1");
        store.put("key1", "val2");
        assertEquals("val2", store.get("key1"));
    }

    @Test
    public void testFlush() {
        KeyValueStoreLsm store = new KeyValueStoreLsm(testDir, 2);
        store.put("key1", "val1");
        store.put("key2", "val2"); // Threshold reached, flushes
        store.put("key3", "val3");

        assertEquals("val1", store.get("key1"));
        assertEquals("val2", store.get("key2"));
        assertEquals("val3", store.get("key3"));
    }

    @Test
    public void testDelete() {
        KeyValueStoreLsm store = new KeyValueStoreLsm(testDir, 2);
        store.put("key1", "val1");
        store.delete("key1");
        assertNull(store.get("key1"));
    }
}
