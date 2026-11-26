import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Coordinates resumable multipart upload sessions.
 * This is an illustrative skeleton for interview-oriented design discussion.
 */
class UploadSessionCoordinator {
    private final Map<String, UploadSessionRecord> sessions = new HashMap<>();

    public String startSession(
            String userId,
            String logicalPath,
            long totalBytes,
            int chunkSizeBytes,
            List<String> expectedChunkHashes) {
        String sessionId = UUID.randomUUID().toString();
        UploadSessionRecord record = new UploadSessionRecord(
                sessionId,
                userId,
                logicalPath,
                totalBytes,
                chunkSizeBytes,
                expectedChunkHashes
        );
        sessions.put(sessionId, record);
        return sessionId;
    }

    public UploadInstruction getChunkUploadInstruction(String sessionId, int chunkIndex) {
        UploadSessionRecord record = requireSession(sessionId);
        record.status = UploadSessionStatus.UPLOADING;
        String uploadUrl = "https://blob.example/upload/" + sessionId + "/" + chunkIndex;
        return new UploadInstruction(chunkIndex, uploadUrl, Instant.now().plusSeconds(900));
    }

    public void markChunkUploaded(String sessionId, int chunkIndex, String checksum, String eTag) {
        UploadSessionRecord record = requireSession(sessionId);
        record.uploadedChecksums.put(chunkIndex, checksum);
        record.uploadedEtags.put(chunkIndex, eTag);
        if (canFinalize(sessionId)) {
            record.status = UploadSessionStatus.READY_TO_FINALIZE;
        }
    }

    public UploadSessionProgress getSessionProgress(String sessionId) {
        UploadSessionRecord record = requireSession(sessionId);
        long uploadedChunks = record.uploadedChecksums.size();
        long uploadedBytes = Math.min(
                record.totalBytes,
                uploadedChunks * (long) record.chunkSizeBytes
        );
        return new UploadSessionProgress((int) uploadedChunks, record.totalChunks(), uploadedBytes);
    }

    public List<Integer> listMissingChunks(String sessionId) {
        UploadSessionRecord record = requireSession(sessionId);
        List<Integer> missing = new ArrayList<>();
        for (int i = 0; i < record.totalChunks(); i++) {
            if (!record.uploadedChecksums.containsKey(i)) {
                missing.add(i);
            }
        }
        return missing;
    }

    public boolean canFinalize(String sessionId) {
        UploadSessionRecord record = requireSession(sessionId);
        return record.uploadedChecksums.size() == record.totalChunks();
    }

    public String finalizeSession(String sessionId) {
        UploadSessionRecord record = requireSession(sessionId);
        if (!canFinalize(sessionId)) {
            throw new IllegalStateException("Upload session is incomplete");
        }
        record.status = UploadSessionStatus.COMPLETED;
        return "blob://" + record.userId + "/" + record.logicalPath;
    }

    public void abortSession(String sessionId, String reason) {
        UploadSessionRecord record = requireSession(sessionId);
        record.status = UploadSessionStatus.FAILED;
        record.failureReason = reason;
    }

    public int expireSessions(Instant now) {
        int expired = 0;
        for (UploadSessionRecord record : sessions.values()) {
            if (record.status == UploadSessionStatus.COMPLETED || record.status == UploadSessionStatus.FAILED) {
                continue;
            }
            if (record.createdAt.plusSeconds(86400).isBefore(now)) {
                record.status = UploadSessionStatus.EXPIRED;
                expired++;
            }
        }
        return expired;
    }

    private UploadSessionRecord requireSession(String sessionId) {
        UploadSessionRecord record = sessions.get(sessionId);
        if (record == null) {
            throw new IllegalArgumentException("Unknown session: " + sessionId);
        }
        return record;
    }

    enum UploadSessionStatus {
        PENDING,
        UPLOADING,
        READY_TO_FINALIZE,
        COMPLETED,
        FAILED,
        EXPIRED
    }

    static class UploadInstruction {
        final int chunkIndex;
        final String uploadUrl;
        final Instant expiresAt;

        UploadInstruction(int chunkIndex, String uploadUrl, Instant expiresAt) {
            this.chunkIndex = chunkIndex;
            this.uploadUrl = uploadUrl;
            this.expiresAt = expiresAt;
        }
    }

    static class UploadSessionProgress {
        final int uploadedChunks;
        final int totalChunks;
        final long uploadedBytes;

        UploadSessionProgress(int uploadedChunks, int totalChunks, long uploadedBytes) {
            this.uploadedChunks = uploadedChunks;
            this.totalChunks = totalChunks;
            this.uploadedBytes = uploadedBytes;
        }
    }

    private static class UploadSessionRecord {
        final String sessionId;
        final String userId;
        final String logicalPath;
        final long totalBytes;
        final int chunkSizeBytes;
        final List<String> expectedChunkHashes;
        final Instant createdAt;
        final Map<Integer, String> uploadedChecksums;
        final Map<Integer, String> uploadedEtags;
        UploadSessionStatus status;
        String failureReason;

        UploadSessionRecord(
                String sessionId,
                String userId,
                String logicalPath,
                long totalBytes,
                int chunkSizeBytes,
                List<String> expectedChunkHashes) {
            this.sessionId = sessionId;
            this.userId = userId;
            this.logicalPath = logicalPath;
            this.totalBytes = totalBytes;
            this.chunkSizeBytes = chunkSizeBytes;
            this.expectedChunkHashes = expectedChunkHashes;
            this.createdAt = Instant.now();
            this.uploadedChecksums = new HashMap<>();
            this.uploadedEtags = new HashMap<>();
            this.status = UploadSessionStatus.PENDING;
        }

        int totalChunks() {
            return expectedChunkHashes.size();
        }
    }
}
