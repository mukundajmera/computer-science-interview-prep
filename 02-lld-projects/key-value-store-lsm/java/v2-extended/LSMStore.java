import java.io.*;
import java.nio.charset.StandardCharsets;
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
        ssTables.add(0, sstFile);
        memTable = new ConcurrentSkipListMap<>();
        if (walFile.exists()) {
            walFile.delete();
        }
    }

    public String get(String key) {
        String val = memTable.get(key);
        if (val != null) {
            return val.equals(TOMBSTONE) ? null : val;
        }

        for (File sst : ssTables) {
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
