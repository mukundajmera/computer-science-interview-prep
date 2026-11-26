import java.io.*;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicLong;

public class LSMStore {
    private ConcurrentSkipListMap<String, String> memTable;
    private final File walFile;
    private final File dataDir;
    private final int memTableThreshold;
    private final List<File> ssTables;
    private static final String TOMBSTONE = "<TOMBSTONE>";
    private final AtomicLong fileCounter = new AtomicLong(System.currentTimeMillis());
    public Runnable flushCrashPoint = null;
    public Runnable appendCrashPoint = null;
    private final Map<File, Long> bloomFilters = new java.util.concurrent.ConcurrentHashMap<>();

    private int getBloomHash(String key) {
        int hash = 0;
        for (char c : key.toCharArray()) hash += c;
        return hash % 64;
    }

    private void updateBloomFilter(File sstFile) {
        long filter = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(sstFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("=", 2);
                if (parts.length == 2) {
                    filter |= (1L << getBloomHash(parts[0]));
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        bloomFilters.put(sstFile, filter);
    }

    public LSMStore(String dir, int threshold) {
        this.memTable = new ConcurrentSkipListMap<>();
        this.dataDir = new File(dir);
        this.memTableThreshold = threshold;
        this.ssTables = new CopyOnWriteArrayList<>();
        if (!dataDir.exists()) {
            dataDir.mkdirs();
        }
        this.walFile = new File(dataDir, "wal.log");
        loadSSTables();
        recover();
    }

    private void loadSSTables() {
        File[] files = dataDir.listFiles((d, name) -> name.endsWith(".sst"));
        if (files != null) {
            Arrays.sort(files, Comparator.comparingLong(File::lastModified).reversed());
            ssTables.addAll(Arrays.asList(files));
            for (File file : ssTables) {
                updateBloomFilter(file);
            }
        }
    }

    private void recover() {
        if (!walFile.exists()) return;
        try (BufferedReader reader = new BufferedReader(new FileReader(walFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("=", 2);
                if (parts.length == 2) {
                    memTable.put(parts[0], parts[1]);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        checkFlush();
    }

    public synchronized void put(String key, String value) {
        if (appendCrashPoint != null) appendCrashPoint.run();
        try {
            try (FileWriter fw = new FileWriter(walFile, true)) {
                fw.write(key + "=" + value + "\n");
            }
        } catch (IOException e) {
            throw new RuntimeException("WAL write failed", e);
        }
        memTable.put(key, value);
        checkFlush();
    }

    public synchronized void delete(String key) {
        put(key, TOMBSTONE);
    }

    private void checkFlush() {
        if (memTable.size() >= memTableThreshold) {
            flush();
        }
    }

    private void flush() {
        if (memTable.isEmpty()) return;
        File sstFile = new File(dataDir, fileCounter.incrementAndGet() + ".sst");
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(sstFile))) {
            for (Map.Entry<String, String> entry : memTable.entrySet()) {
                writer.write(entry.getKey() + "=" + entry.getValue() + "\n");
            }
        } catch (IOException e) {
            throw new RuntimeException("Flush failed", e);
        }
        if (flushCrashPoint != null) flushCrashPoint.run();
        updateBloomFilter(sstFile);
        ssTables.add(0, sstFile);
        memTable = new ConcurrentSkipListMap<>();
        if (walFile.exists()) {
            walFile.delete();
        }
        
        if (ssTables.size() > 2) {
            compact();
        }
    }

    private void compact() {
        Map<String, String> merged = new TreeMap<>();
        for (int i = ssTables.size() - 1; i >= 0; i--) {
            File sst = ssTables.get(i);
            try (BufferedReader reader = new BufferedReader(new FileReader(sst))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("=", 2);
                    if (parts.length == 2) {
                        merged.put(parts[0], parts[1]);
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        File compactedFile = new File(dataDir, fileCounter.incrementAndGet() + "_compacted.sst");
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(compactedFile))) {
            for (Map.Entry<String, String> entry : merged.entrySet()) {
                writer.write(entry.getKey() + "=" + entry.getValue() + "\n");
            }
        } catch (IOException e) {
            throw new RuntimeException("Compact failed", e);
        }

        for (File sst : ssTables) {
            sst.delete();
            bloomFilters.remove(sst);
        }
        ssTables.clear();
        updateBloomFilter(compactedFile);
        ssTables.add(compactedFile);
    }

    public String get(String key) {
        String val = memTable.get(key);
        if (val != null) {
            return val.equals(TOMBSTONE) ? null : val;
        }

        for (File sst : ssTables) {
            Long filter = bloomFilters.get(sst);
            if (filter != null && (filter & (1L << getBloomHash(key))) == 0) {
                continue;
            }
            try (BufferedReader reader = new BufferedReader(new FileReader(sst))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("=", 2);
                    if (parts.length == 2 && parts[0].equals(key)) {
                        return parts[1].equals(TOMBSTONE) ? null : parts[1];
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return null;
    }
}
