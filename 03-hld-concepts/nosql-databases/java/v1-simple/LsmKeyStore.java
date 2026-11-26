import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

public class LsmKeyStore {

    private final int memtableThreshold;
    private final Path dataDir;
    private SortedMap<String, String> memtable;
    private final Path walFile;
    private final List<SSTable> ssTables;
    private int ssTableCounter;

    public LsmKeyStore(int memtableThreshold, String dataDirPath) throws IOException {
        this.memtableThreshold = memtableThreshold;
        this.dataDir = Paths.get(dataDirPath);
        Files.createDirectories(this.dataDir);
        this.memtable = new TreeMap<>();
        this.walFile = this.dataDir.resolve("wal.log");
        this.ssTables = new ArrayList<>();
        this.ssTableCounter = 0;
        recover();
    }

    private void recover() throws IOException {
        if (Files.exists(walFile)) {
            List<String> lines = Files.readAllLines(walFile, StandardCharsets.UTF_8);
            for (String line : lines) {
                if (line.trim().isEmpty()) continue;
                String[] parts = line.split(":", 2);
                if (parts.length == 2) {
                    String key = parts[0];
                    String value = parts[1].equals("NULL") ? null : parts[1];
                    memtable.put(key, value);
                }
            }
            if (memtable.size() >= memtableThreshold) {
                flushMemtable();
            }
        }
    }

    private void appendWal(String key, String value) throws IOException {
        String valStr = value == null ? "NULL" : value;
        String line = key + ":" + valStr + System.lineSeparator();
        Files.write(walFile, line.getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }

    private void flushMemtable() throws IOException {
        if (memtable.isEmpty()) return;

        String filename = "sstable_" + ssTableCounter + ".txt";
        Path ssTablePath = dataDir.resolve(filename);
        ssTableCounter++;

        SSTable ssTable = new SSTable(ssTablePath, memtable);
        ssTables.add(0, ssTable); // Add to the front so newest is searched first

        memtable = new TreeMap<>();
        Files.deleteIfExists(walFile);
    }

    public void put(String key, String value) throws IOException {
        appendWal(key, value);
        memtable.put(key, value);
        if (memtable.size() >= memtableThreshold) {
            flushMemtable();
        }
    }

    public void delete(String key) throws IOException {
        appendWal(key, null);
        memtable.put(key, null); // Tombstone
        if (memtable.size() >= memtableThreshold) {
            flushMemtable();
        }
    }

    public String get(String key) throws IOException {
        if (memtable.containsKey(key)) {
            return memtable.get(key);
        }

        for (SSTable ssTable : ssTables) {
            SearchResult result = ssTable.get(key);
            if (result.found) {
                return result.value;
            }
        }

        return null;
    }

    public List<Map.Entry<String, String>> scan(String startKey, String endKey) throws IOException {
        SortedMap<String, String> merged = new TreeMap<>();

        // Read from oldest to newest SSTables to overwrite older values
        for (int i = ssTables.size() - 1; i >= 0; i--) {
            SSTable ssTable = ssTables.get(i);
            for (Map.Entry<String, String> entry : ssTable.scan(startKey, endKey)) {
                merged.put(entry.getKey(), entry.getValue());
            }
        }

        // Finally, merge memtable values
        for (Map.Entry<String, String> entry : memtable.entrySet()) {
            if (entry.getKey().compareTo(startKey) >= 0 && entry.getKey().compareTo(endKey) <= 0) {
                merged.put(entry.getKey(), entry.getValue());
            }
        }

        List<Map.Entry<String, String>> result = new ArrayList<>();
        for (Map.Entry<String, String> entry : merged.entrySet()) {
            if (entry.getValue() != null) {
                result.add(entry);
            }
        }

        return result;
    }

    // Static nested classes for internal use
    private static class SearchResult {
        final boolean found;
        final String value;
        SearchResult(boolean found, String value) {
            this.found = found;
            this.value = value;
        }
    }

    private static class BloomFilter {
        private final int size;
        private final int hashCount;
        private final boolean[] bitArray;

        BloomFilter(int size, int hashCount) {
            this.size = size;
            this.hashCount = hashCount;
            this.bitArray = new boolean[size];
        }

        private int[] getHashes(String item) {
            int[] hashes = new int[hashCount];
            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                for (int i = 0; i < hashCount; i++) {
                    byte[] hashBytes = digest.digest((item + i).getBytes(StandardCharsets.UTF_8));
                    int hashInt = Math.abs(java.nio.ByteBuffer.wrap(hashBytes).getInt());
                    hashes[i] = hashInt % size;
                }
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException("SHA-256 algorithm not found", e);
            }
            return hashes;
        }

        void add(String item) {
            for (int h : getHashes(item)) {
                bitArray[h] = true;
            }
        }

        boolean mightContain(String item) {
            for (int h : getHashes(item)) {
                if (!bitArray[h]) {
                    return false;
                }
            }
            return true;
        }
    }

    private static class SSTable {
        private final Path filePath;
        private final BloomFilter bloomFilter;
        private final Map<String, Integer> index;

        SSTable(Path filePath, SortedMap<String, String> data) throws IOException {
            this.filePath = filePath;
            this.bloomFilter = new BloomFilter(Math.max(100, data.size() * 10), 3);
            this.index = new HashMap<>();

            writeToDisk(data);
        }

        private void writeToDisk(SortedMap<String, String> data) throws IOException {
            try (BufferedWriter writer = Files.newBufferedWriter(filePath, StandardCharsets.UTF_8)) {
                int lineNumber = 0;
                for (Map.Entry<String, String> entry : data.entrySet()) {
                    String k = entry.getKey();
                    String v = entry.getValue() == null ? "NULL" : entry.getValue();

                    bloomFilter.add(k);
                    index.put(k, lineNumber);

                    writer.write(k + ":" + v);
                    writer.newLine();
                    lineNumber++;
                }
            }
        }

        private List<Map.Entry<String, String>> readFromDisk() throws IOException {
            List<Map.Entry<String, String>> data = new ArrayList<>();
            if (!Files.exists(filePath)) return data;

            List<String> lines = Files.readAllLines(filePath, StandardCharsets.UTF_8);
            for (String line : lines) {
                String[] parts = line.split(":", 2);
                if (parts.length == 2) {
                    String value = parts[1].equals("NULL") ? null : parts[1];
                    data.add(new AbstractMap.SimpleEntry<>(parts[0], value));
                }
            }
            return data;
        }

        SearchResult get(String key) throws IOException {
            if (!bloomFilter.mightContain(key)) {
                return new SearchResult(false, null);
            }

            if (index.containsKey(key)) {
                int lineNum = index.get(key);
                List<Map.Entry<String, String>> data = readFromDisk();
                if (lineNum < data.size() && data.get(lineNum).getKey().equals(key)) {
                    return new SearchResult(true, data.get(lineNum).getValue());
                }
            }

            return new SearchResult(false, null);
        }

        List<Map.Entry<String, String>> scan(String startKey, String endKey) throws IOException {
            List<Map.Entry<String, String>> result = new ArrayList<>();
            List<Map.Entry<String, String>> data = readFromDisk();

            for (Map.Entry<String, String> entry : data) {
                String k = entry.getKey();
                if (k.compareTo(startKey) >= 0 && k.compareTo(endKey) <= 0) {
                    result.add(entry);
                }
            }
            return result;
        }
    }
}
