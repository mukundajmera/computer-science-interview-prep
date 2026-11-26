package keyvaluestore;

import java.util.*;

class WAL {
    List<Map.Entry<String, String>> entries = new ArrayList<>();
    
    void append(String key, String value) {
        entries.add(new AbstractMap.SimpleEntry<>(key, value));
    }
}

class LSMStore {
    Map<String, String> memtable = new HashMap<>();
    WAL wal = new WAL();
    
    void put(String key, String value) {
        wal.append(key, value);
        memtable.put(key, value);
    }
    
    String get(String key) {
        return memtable.get(key);
    }
}

public class KVStoreV1 {
    public static void main(String[] args) {
        testPutGet();
        testOverwrite();
        testNotFound();
        testWalAppend();
        testMultiplePuts();
        testWalMultiple();
        System.out.println("V1 Tests passed");
    }
    
    static void testPutGet() {
        LSMStore store = new LSMStore();
        store.put("k1", "v1");
        assert "v1".equals(store.get("k1"));
    }
    
    static void testOverwrite() {
        LSMStore store = new LSMStore();
        store.put("k1", "v1");
        store.put("k1", "v2");
        assert "v2".equals(store.get("k1"));
    }
    
    static void testNotFound() {
        LSMStore store = new LSMStore();
        assert store.get("k2") == null;
    }
    
    static void testWalAppend() {
        LSMStore store = new LSMStore();
        store.put("k1", "v1");
        assert store.wal.entries.size() == 1;
    }
    
    static void testMultiplePuts() {
        LSMStore store = new LSMStore();
        for (int i=0; i<10; i++) store.put("k"+i, "v"+i);
        assert "v5".equals(store.get("k5"));
    }
    
    static void testWalMultiple() {
        LSMStore store = new LSMStore();
        for (int i=0; i<5; i++) store.put("k"+i, "v"+i);
        assert store.wal.entries.size() == 5;
    }
}
