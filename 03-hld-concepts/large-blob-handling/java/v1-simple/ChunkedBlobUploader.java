import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class ChunkedBlobUploader {

    public static class UploadSession {
        private final String sessionId;
        private final String blobId;
        private final int totalChunks;
        private final long totalSize;
        private final String expectedSha256;
        private final Map<Integer, byte[]> chunks;
        private boolean isCompleted;

        public UploadSession(String sessionId, String blobId, int totalChunks, long totalSize, String expectedSha256) {
            this.sessionId = sessionId;
            this.blobId = blobId;
            this.totalChunks = totalChunks;
            this.totalSize = totalSize;
            this.expectedSha256 = expectedSha256;
            this.chunks = new ConcurrentHashMap<>();
            this.isCompleted = false;
        }

        public String getSessionId() { return sessionId; }
        public String getBlobId() { return blobId; }
        public int getTotalChunks() { return totalChunks; }
        public long getTotalSize() { return totalSize; }
        public String getExpectedSha256() { return expectedSha256; }
        public boolean isCompleted() { return isCompleted; }

        public void addChunk(int chunkIndex, byte[] data) {
            if (isCompleted) {
                throw new IllegalStateException("Session already completed");
            }
            if (chunkIndex < 0 || chunkIndex >= totalChunks) {
                throw new IllegalArgumentException("Invalid chunk index");
            }
            chunks.put(chunkIndex, data);
        }

        public List<Integer> getMissingChunks() {
            List<Integer> missing = new ArrayList<>();
            for (int i = 0; i < totalChunks; i++) {
                if (!chunks.containsKey(i)) {
                    missing.add(i);
                }
            }
            return missing;
        }

        public boolean hasAllChunks() {
            return chunks.size() == totalChunks;
        }

        public byte[] assemble() {
            if (!hasAllChunks()) {
                throw new IllegalStateException("Cannot assemble, missing chunks");
            }
            byte[] assembled = new byte[(int) totalSize];
            int offset = 0;
            for (int i = 0; i < totalChunks; i++) {
                byte[] chunk = chunks.get(i);
                System.arraycopy(chunk, 0, assembled, offset, chunk.length);
                offset += chunk.length;
            }
            this.isCompleted = true;
            return assembled;
        }
    }

    private final Map<String, UploadSession> sessions = new ConcurrentHashMap<>();
    private final Map<String, byte[]> completedBlobs = new ConcurrentHashMap<>();

    public String initiateSession(String blobId, int totalChunks, long totalSize, String expectedSha256) {
        String sessionId = UUID.randomUUID().toString();
        UploadSession session = new UploadSession(sessionId, blobId, totalChunks, totalSize, expectedSha256);
        sessions.put(sessionId, session);
        return sessionId;
    }

    public void uploadChunk(String sessionId, int chunkIndex, byte[] data) {
        UploadSession session = sessions.get(sessionId);
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID");
        }
        session.addChunk(chunkIndex, data);
    }

    public List<Integer> getMissingChunks(String sessionId) {
        UploadSession session = sessions.get(sessionId);
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID");
        }
        return session.getMissingChunks();
    }

    public boolean completeSession(String sessionId) {
        UploadSession session = sessions.get(sessionId);
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID");
        }
        if (!session.hasAllChunks()) {
            return false;
        }

        byte[] assembled = session.assemble();
        String actualSha256 = computeSha256(assembled);

        if (!actualSha256.equals(session.getExpectedSha256())) {
            throw new IllegalStateException("Checksum mismatch");
        }

        completedBlobs.put(session.getBlobId(), assembled);
        sessions.remove(sessionId);
        return true;
    }

    public byte[] getBlob(String blobId) {
        return completedBlobs.get(blobId);
    }

    public static String computeSha256(byte[] data) {
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
            throw new RuntimeException("SHA-256 not supported", e);
        }
    }
}
