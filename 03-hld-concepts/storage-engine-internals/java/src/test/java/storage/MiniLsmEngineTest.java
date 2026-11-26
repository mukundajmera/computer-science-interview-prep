package storage;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MiniLsmEngineTest {

    @Test
    public void testInMemoryRetrieval() {
        MiniLsmEngine engine = new MiniLsmEngine(1000); // large threshold to avoid flush
        engine.put("key1", "value1");
        engine.put("key2", "value2");

        assertEquals("value1", engine.get("key1"));
        assertEquals("value2", engine.get("key2"));
        assertNull(engine.get("key3"));
        assertEquals(0, engine.getSsTablesCount());
    }

    @Test
    public void testSSTablePointLookupAfterFlush() {
        MiniLsmEngine engine = new MiniLsmEngine(10); // very small threshold to force flush
        
        engine.put("key1", "val1"); // 8 bytes -> memTableSize = 8
        engine.put("key2", "val2"); // 8 bytes -> triggers flush before put, memTableSize = 8, ssTables = 1

        assertEquals("val1", engine.get("key1"));
        assertEquals("val2", engine.get("key2"));
        assertTrue(engine.getSsTablesCount() >= 1);
    }

    @Test
    public void testTombstoneDeletion() {
        MiniLsmEngine engine = new MiniLsmEngine(100);
        
        engine.put("key1", "value1");
        assertEquals("value1", engine.get("key1"));
        
        engine.delete("key1");
        assertNull(engine.get("key1"));

        // Force flush and check again to ensure tombstone is handled in SSTable
        engine.put("key2", "value2");
        engine.put("key3", "value3");
        engine.put("key4", "value4"); // Might trigger flush depending on threshold
        
        assertNull(engine.get("key1"));
    }

    @Test
    public void testCompactionDeduplication() {
        MiniLsmEngine engine = new MiniLsmEngine(15);
        
        // Write keys that will be flushed to multiple SSTables
        engine.put("key1", "v1");
        engine.put("key2", "v2"); // Flushes key1
        engine.put("key1", "v1-new"); // Overwrite key1
        engine.put("key3", "v3"); // Flushes key2, key1-new
        engine.delete("key2");    // Tombstone for key2
        engine.put("key4", "v4"); // Flushes key3, key2-tombstone
        
        // Assert state before compaction
        assertEquals("v1-new", engine.get("key1"));
        assertNull(engine.get("key2"));
        assertEquals("v3", engine.get("key3"));
        assertTrue(engine.getSsTablesCount() > 1);
        
        engine.compact();
        
        // Assert state after compaction
        assertEquals(1, engine.getSsTablesCount());
        assertEquals("v1-new", engine.get("key1"));
        assertNull(engine.get("key2"));
        assertEquals("v3", engine.get("key3"));
        assertEquals("v4", engine.get("key4"));
    }

    @Test
    public void testBloomFilterSkipping() {
        MiniLsmEngine.BloomFilter bloomFilter = new MiniLsmEngine.BloomFilter(100, 3);
        bloomFilter.add("existing_key");
        
        assertTrue(bloomFilter.mightContain("existing_key"));
        // While theoretically possible to collide, a 100-bit filter with 1 item and 3 hashes
        // has an extremely low false positive rate for a single different key.
        assertFalse(bloomFilter.mightContain("non_existing_key"));
    }
}
