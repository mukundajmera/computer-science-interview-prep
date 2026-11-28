import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

/**
 * v2 ChunkServer: self-describing container frames plus index rebuild.
 *
 * Each chunk is stored as a length-prefixed frame (magic + chunk id + size +
 * payload) instead of v1's raw bytes, so the in-memory index can always be
 * reconstructed by scanning the container file. This is v2 improvement #2;
 * see ObjectStorageServiceV2's javadoc for the full list.
 */
public class ChunkServerV2 {
    private static final int MAGIC = 0x43484B31; // "CHK1"

    private final String serverId;
    private final String dataDir;
    private final File containerFile;
    private final ReentrantLock lock;
    private final Map<String, ChunkInfo> index;
    private volatile boolean down;

    public static class ChunkInfo {
        public final long offset;
        public final int size;
        public final String checksum;

        public ChunkInfo(long offset, int size, String checksum) {
            this.offset = offset;
            this.size = size;
            this.checksum = checksum;
        }
    }

    public ChunkServerV2(String dataDir, String serverId) throws IOException {
        this.serverId = serverId;
        this.dataDir = dataDir;
        this.containerFile = new File(dataDir, serverId + "_container.dat");
        this.lock = new ReentrantLock();
        this.index = new ConcurrentHashMap<>();
        Files.createDirectories(Paths.get(dataDir));
        if (!this.containerFile.exists()) {
            this.containerFile.createNewFile();
        }
        // A restart never trusts memory: the index always comes from a scan.
        rebuildIndexFromContainer();
    }

    private String calculateChecksum(byte[] data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(data);
            StringBuilder hexString = new StringBuilder(2 * hash.length);
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    private void checkUp() {
        if (down) {
            throw new IllegalStateException("Chunk server " + serverId + " is down");
        }
    }

    private void writeFrame(RandomAccessFile raf, String chunkId, byte[] data) throws IOException {
        byte[] idBytes = chunkId.getBytes(StandardCharsets.UTF_8);
        raf.seek(raf.length());
        raf.writeInt(MAGIC);
        raf.writeInt(idBytes.length);
        raf.write(idBytes);
        raf.writeLong(data.length);
        raf.write(data);
    }

    public ChunkInfo writeChunk(String chunkId, byte[] data) throws IOException {
        checkUp();
        String checksum = calculateChecksum(data);
        lock.lock();
        try {
            if (index.containsKey(chunkId)) {
                throw new IllegalArgumentException("Chunk " + chunkId + " already exists");
            }
            long dataOffset;
            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "rw")) {
                writeFrame(raf, chunkId, data);
                dataOffset = raf.length() - data.length;
            }
            ChunkInfo info = new ChunkInfo(dataOffset, data.length, checksum);
            index.put(chunkId, info);
            return info;
        } finally {
            lock.unlock();
        }
    }

    public byte[] readChunk(String chunkId) throws IOException {
        checkUp();
        lock.lock();
        try {
            if (!index.containsKey(chunkId)) {
                throw new IllegalArgumentException("Chunk " + chunkId + " not found");
            }
            ChunkInfo info = index.get(chunkId);
            byte[] data = new byte[info.size];
            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "r")) {
                raf.seek(info.offset);
                raf.readFully(data);
            }
            if (!calculateChecksum(data).equals(info.checksum)) {
                throw new IllegalStateException("Checksum mismatch for chunk " + chunkId);
            }
            return data;
        } finally {
            lock.unlock();
        }
    }

    public void repairChunk(String chunkId, byte[] data) throws IOException {
        checkUp();
        String checksum = calculateChecksum(data);
        lock.lock();
        try {
            long dataOffset;
            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "rw")) {
                writeFrame(raf, chunkId, data);
                dataOffset = raf.length() - data.length;
            }
            index.put(chunkId, new ChunkInfo(dataOffset, data.length, checksum));
        } finally {
            lock.unlock();
        }
    }

    public boolean hasChunk(String chunkId) {
        return index.containsKey(chunkId);
    }

    public ChunkInfo getChunkInfo(String chunkId) {
        lock.lock();
        try {
            if (!index.containsKey(chunkId)) {
                throw new IllegalArgumentException("Chunk " + chunkId + " not found");
            }
            return index.get(chunkId);
        } finally {
            lock.unlock();
        }
    }

    public String getServerId() {
        return serverId;
    }

    public File getContainerFile() {
        return containerFile;
    }

    /** Failure injection: simulate the whole server being unreachable. */
    public void setDown(boolean down) {
        this.down = down;
    }

    public boolean isDown() {
        return down;
    }

    /**
     * Failure injection: a disk sector loses this one chunk. The stale bytes
     * stay in the container until compaction, like a real partial disk failure.
     */
    public void simulateChunkLoss(String chunkId) {
        index.remove(chunkId);
    }

    /**
     * Scans the container file and reconstructs the index from the frame
     * headers, answering the FOLLOW-UPS.md probe about local index
     * corruption. Stops cleanly at the first torn or corrupt tail frame.
     * Returns the number of chunks recovered.
     */
    public int rebuildIndexFromContainer() throws IOException {
        lock.lock();
        try {
            Map<String, ChunkInfo> newIndex = new ConcurrentHashMap<>();
            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "r")) {
                while (raf.getFilePointer() + 8 <= raf.length()) {
                    if (raf.readInt() != MAGIC) {
                        break;
                    }
                    int idLen = raf.readInt();
                    byte[] idBytes = new byte[idLen];
                    raf.readFully(idBytes);
                    if (raf.getFilePointer() + 8 > raf.length()) {
                        break;
                    }
                    long dataLen = raf.readLong();
                    long dataOffset = raf.getFilePointer();
                    if (dataLen < 0 || dataLen > Integer.MAX_VALUE
                            || raf.length() - dataOffset < dataLen) {
                        break;
                    }
                    byte[] data = new byte[(int) dataLen];
                    raf.readFully(data);
                    newIndex.put(new String(idBytes, StandardCharsets.UTF_8),
                            new ChunkInfo(dataOffset, (int) dataLen, calculateChecksum(data)));
                }
            }
            index.clear();
            index.putAll(newIndex);
            return newIndex.size();
        } finally {
            lock.unlock();
        }
    }

    public void compact(Set<String> activeChunks) throws IOException {
        lock.lock();
        try {
            File newContainer = new File(dataDir, serverId + "_container_new.dat");
            Map<String, ChunkInfo> newIndex = new ConcurrentHashMap<>();
            try (RandomAccessFile inRaf = new RandomAccessFile(containerFile, "r");
                 RandomAccessFile outRaf = new RandomAccessFile(newContainer, "rw")) {
                for (Map.Entry<String, ChunkInfo> entry : index.entrySet()) {
                    if (activeChunks.contains(entry.getKey())) {
                        ChunkInfo info = entry.getValue();
                        byte[] data = new byte[info.size];
                        inRaf.seek(info.offset);
                        inRaf.readFully(data);
                        writeFrame(outRaf, entry.getKey(), data);
                        long dataOffset = outRaf.length() - info.size;
                        newIndex.put(entry.getKey(), new ChunkInfo(dataOffset, info.size, info.checksum));
                    }
                }
            }
            Files.move(newContainer.toPath(), containerFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
            index.clear();
            index.putAll(newIndex);
        } finally {
            lock.unlock();
        }
    }
}
