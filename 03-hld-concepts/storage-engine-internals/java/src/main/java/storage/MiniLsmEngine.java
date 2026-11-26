package storage;

import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.ConcurrentSkipListMap;

public class MiniLsmEngine {

    private final int memTableThreshold;
    private ConcurrentSkipListMap<String, String> memTable;
    private int currentMemTableSize;
    private final List<SSTable> ssTables;

    // Tombstone marker for deleted keys
    public static final String TOMBSTONE = "<TOMBSTONE>";

    public MiniLsmEngine(int memTableThreshold) {
        this.memTableThreshold = memTableThreshold;
        this.memTable = new ConcurrentSkipListMap<>();
        this.currentMemTableSize = 0;
        this.ssTables = new ArrayList<>();
    }

    public synchronized void put(String key, String value) {
        int entrySize = key.getBytes(StandardCharsets.UTF_8).length + value.getBytes(StandardCharsets.UTF_8).length;
        if (currentMemTableSize + entrySize > memTableThreshold) {
            flush();
        }
        memTable.put(key, value);
        currentMemTableSize += entrySize;
    }

    public synchronized void delete(String key) {
        put(key, TOMBSTONE);
    }

    public synchronized String get(String key) {
        // First, check the MemTable
        String value = memTable.get(key);
        if (value != null) {
            if (value.equals(TOMBSTONE)) {
                return null;
            }
            return value;
        }

        // Second, check SSTables from newest to oldest
        for (int i = ssTables.size() - 1; i >= 0; i--) {
            SSTable table = ssTables.get(i);
            if (table.mightContain(key)) {
                String ssValue = table.get(key);
                if (ssValue != null) {
                    if (ssValue.equals(TOMBSTONE)) {
                        return null;
                    }
                    return ssValue;
                }
            }
        }

        return null;
    }

    private void flush() {
        if (memTable.isEmpty()) {
            return;
        }
        SSTable newTable = new SSTable(memTable);
        ssTables.add(newTable);
        memTable = new ConcurrentSkipListMap<>();
        currentMemTableSize = 0;
    }

    public synchronized void compact() {
        flush(); // flush any remaining data

        if (ssTables.size() <= 1) {
            return;
        }

        Map<String, String> mergedData = new TreeMap<>();
        // Merge from oldest to newest, so newer keys overwrite older ones
        for (SSTable table : ssTables) {
            for (Map.Entry<String, String> entry : table.getData().entrySet()) {
                mergedData.put(entry.getKey(), entry.getValue());
            }
        }

        // Remove tombstones during compaction
        mergedData.entrySet().removeIf(entry -> entry.getValue().equals(TOMBSTONE));

        SSTable compactedTable = new SSTable(new ConcurrentSkipListMap<>(mergedData));
        ssTables.clear();
        ssTables.add(compactedTable);
    }

    // Returns internal state size for testing
    public int getSsTablesCount() {
        return ssTables.size();
    }

    // Inner class representing an SSTable
    static class SSTable {
        private final Map<String, String> data;
        private final List<String> sparseIndex;
        private final BloomFilter bloomFilter;
        private static final int BLOCK_SIZE = 2; // For demonstration, block size in terms of keys

        public SSTable(SortedMap<String, String> data) {
            this.data = new TreeMap<>(data); // Immutable copy
            this.sparseIndex = new ArrayList<>();
            this.bloomFilter = new BloomFilter(100, 3); // Arbitrary size for demo

            int count = 0;
            for (String key : this.data.keySet()) {
                if (count % BLOCK_SIZE == 0) {
                    sparseIndex.add(key);
                }
                bloomFilter.add(key);
                count++;
            }
        }

        public boolean mightContain(String key) {
            return bloomFilter.mightContain(key);
        }

        public String get(String key) {
            // Use sparse index to find the block (in a real system this would seek on disk)
            if (sparseIndex.isEmpty()) return null;
            
            // Just return from our TreeMap representing the disk data
            return data.get(key);
        }

        public Map<String, String> getData() {
            return Collections.unmodifiableMap(data);
        }
    }

    // Inner class representing a simple Bloom Filter
    static class BloomFilter {
        private final BitSet bitSet;
        private final int size;
        private final int numHashes;

        public BloomFilter(int size, int numHashes) {
            this.size = size;
            this.numHashes = numHashes;
            this.bitSet = new BitSet(size);
        }

        public void add(String key) {
            for (int i = 0; i < numHashes; i++) {
                int hash = getHash(key, i);
                bitSet.set(hash);
            }
        }

        public boolean mightContain(String key) {
            for (int i = 0; i < numHashes; i++) {
                int hash = getHash(key, i);
                if (!bitSet.get(hash)) {
                    return false;
                }
            }
            return true;
        }

        private int getHash(String key, int i) {
            int hash = key.hashCode() ^ (i * 0x5bd1e995);
            return Math.abs(hash) % size;
        }
    }
}
