import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.lang.reflect.Field;

import static org.junit.jupiter.api.Assertions.*;

public class LsmKeyStoreTest {

    private static final String TEST_DIR = "test_lsm_data";
    private LsmKeyStore store;

    @BeforeEach
    public void setUp() throws IOException {
        cleanUpDir(Paths.get(TEST_DIR));
        store = new LsmKeyStore(3, TEST_DIR);
    }

    @AfterEach
    public void tearDown() throws IOException {
        cleanUpDir(Paths.get(TEST_DIR));
    }

    private void cleanUpDir(Path path) throws IOException {
        if (Files.exists(path)) {
            Files.walk(path)
                 .sorted(Comparator.reverseOrder())
                 .map(Path::toFile)
                 .forEach(File::delete);
        }
    }

    @Test
    public void testPutAndGet() throws IOException {
        store.put("key1", "value1");
        store.put("key2", "value2");

        assertEquals("value1", store.get("key1"));
        assertEquals("value2", store.get("key2"));
        assertNull(store.get("missing"));
    }

    @Test
    public void testDelete() throws IOException {
        store.put("key1", "value1");
        store.delete("key1");

        assertNull(store.get("key1"));
    }

    @Test
    public void testSSTableFlush() throws Exception {
        store.put("k1", "v1");
        store.put("k2", "v2");
        store.put("k3", "v3"); // This should trigger a flush

        Field ssTablesField = LsmKeyStore.class.getDeclaredField("ssTables");
        ssTablesField.setAccessible(true);
        List<?> ssTables = (List<?>) ssTablesField.get(store);

        assertEquals(1, ssTables.size(), "One SSTable should have been created");

        // Data should still be retrievable
        assertEquals("v1", store.get("k1"));
        assertEquals("v2", store.get("k2"));
        assertEquals("v3", store.get("k3"));
    }

    @Test
    public void testScan() throws IOException {
        store.put("a", "1");
        store.put("b", "2");
        store.put("c", "3"); // flush
        store.put("d", "4");
        store.put("e", "5");

        // Overwrite and delete
        store.put("c", "33");
        store.delete("d");

        List<Map.Entry<String, String>> results = store.scan("b", "e");

        assertEquals(3, results.size());
        assertEquals("b", results.get(0).getKey());
        assertEquals("2", results.get(0).getValue());

        assertEquals("c", results.get(1).getKey());
        assertEquals("33", results.get(1).getValue());

        assertEquals("e", results.get(2).getKey());
        assertEquals("5", results.get(2).getValue());
    }

    @Test
    public void testWalRecovery() throws IOException {
        String recoveryDir = "test_lsm_recovery_data";
        cleanUpDir(Paths.get(recoveryDir));

        LsmKeyStore s1 = new LsmKeyStore(5, recoveryDir);
        s1.put("r1", "rv1");
        s1.put("r2", "rv2");

        // Create new store instance with same dir to simulate recovery
        LsmKeyStore s2 = new LsmKeyStore(5, recoveryDir);
        assertEquals("rv1", s2.get("r1"));
        assertEquals("rv2", s2.get("r2"));

        cleanUpDir(Paths.get(recoveryDir));
    }
}
