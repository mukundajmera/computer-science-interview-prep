import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Set;
import java.util.Map;

public class ChunkServer {
    private final String serverId;
    private final String dataDir;
    private final File containerFile;
    private final ReentrantLock lock;
    private final Map<String, ChunkInfo> index;

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

    public ChunkServer(String dataDir, String serverId) throws IOException {
        this.serverId = serverId;
        this.dataDir = dataDir;
        this.containerFile = new File(dataDir, serverId + "_container.dat");
        this.lock = new ReentrantLock();
        this.index = new ConcurrentHashMap<>();

        Files.createDirectories(Paths.get(dataDir));
        if (!this.containerFile.exists()) {
            this.containerFile.createNewFile();
        }
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

    public ChunkInfo writeChunk(String chunkId, byte[] data) throws IOException {
        String checksum = calculateChecksum(data);
        lock.lock();
        try {
            if (index.containsKey(chunkId)) {
                throw new IllegalArgumentException("Chunk " + chunkId + " already exists");
            }
            
            long offset;
            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "rw")) {
                offset = raf.length();
                raf.seek(offset);
                raf.write(data);
            }
            
            ChunkInfo info = new ChunkInfo(offset, data.length, checksum);
            index.put(chunkId, info);
            return info;
        } finally {
            lock.unlock();
        }
    }

    public byte[] readChunk(String chunkId) throws IOException {
        lock.lock();
        try {
            if (!index.containsKey(chunkId)) {
                throw new IllegalArgumentException("Chunk " + chunkId + " not found");
            }

            ChunkInfo info = index.get(chunkId);
            byte[] data = new byte[info.size];

            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "r")) {
                raf.seek(info.offset);
                int bytesRead = raf.read(data);
                if (bytesRead != info.size) {
                    throw new IOException("Incomplete chunk " + chunkId + " read");
                }
            }

            String actualChecksum = calculateChecksum(data);
            if (!actualChecksum.equals(info.checksum)) {
                throw new IllegalStateException("Checksum mismatch for chunk " + chunkId);
            }

            return data;
        } finally {
            lock.unlock();
        }
    }

    public void repairChunk(String chunkId, byte[] data) throws IOException {
        String checksum = calculateChecksum(data);
        lock.lock();
        try {
            long offset;
            try (RandomAccessFile raf = new RandomAccessFile(containerFile, "rw")) {
                offset = raf.length();
                raf.seek(offset);
                raf.write(data);
            }
            index.put(chunkId, new ChunkInfo(offset, data.length, checksum));
        } finally {
            lock.unlock();
        }
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

    public void compact(Set<String> activeChunks) throws IOException {
        lock.lock();
        try {
            File newContainer = new File(dataDir, serverId + "_container_new.dat");
            Map<String, ChunkInfo> newIndex = new ConcurrentHashMap<>();

            try (RandomAccessFile inRaf = new RandomAccessFile(containerFile, "r");
                 RandomAccessFile outRaf = new RandomAccessFile(newContainer, "rw")) {
                
                for (Map.Entry<String, ChunkInfo> entry : index.entrySet()) {
                    String chunkId = entry.getKey();
                    if (activeChunks.contains(chunkId)) {
                        ChunkInfo info = entry.getValue();
                        byte[] data = new byte[info.size];
                        
                        inRaf.seek(info.offset);
                        inRaf.readFully(data);
                        
                        long newOffset = outRaf.length();
                        outRaf.seek(newOffset);
                        outRaf.write(data);
                        
                        newIndex.put(chunkId, new ChunkInfo(newOffset, info.size, info.checksum));
                    }
                }
            }
            
            Files.move(newContainer.toPath(), containerFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
            this.index.clear();
            this.index.putAll(newIndex);
        } finally {
            lock.unlock();
        }
    }
}
