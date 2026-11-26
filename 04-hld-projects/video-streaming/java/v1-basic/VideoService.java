package video.v1;

import java.util.Optional;

public interface VideoService {
    UploadSession initUpload(InitUploadCommand command);
    UploadSession uploadPart(String sessionId, int partNumber, String etag);
    Video completeUpload(String sessionId, String idempotencyKey);
    Optional<Manifest> getManifest(String videoId);
}

enum UploadStatus { INITIATED, PARTIAL, COMPLETING, PROCESSING, READY, FAILED }

final class InitUploadCommand {
    public final String ownerId;
    public final String title;
    public final long totalBytes;
    public final int expectedParts;

    InitUploadCommand(String ownerId, String title, long totalBytes, int expectedParts) {
        this.ownerId = ownerId;
        this.title = title;
        this.totalBytes = totalBytes;
        this.expectedParts = expectedParts;
    }
}

final class UploadSession {
    public final String sessionId;
    public final String videoId;
    public final UploadStatus status;
    public final int expectedParts;
    public final int uploadedParts;

    UploadSession(String sessionId, String videoId, UploadStatus status,
                  int expectedParts, int uploadedParts) {
        this.sessionId = sessionId;
        this.videoId = videoId;
        this.status = status;
        this.expectedParts = expectedParts;
        this.uploadedParts = uploadedParts;
    }
}

final class Video {
    public final String videoId;
    public final String ownerId;
    public final UploadStatus status;

    Video(String videoId, String ownerId, UploadStatus status) {
        this.videoId = videoId;
        this.ownerId = ownerId;
        this.status = status;
    }
}

final class Manifest {
    public final String videoId;
    public final String path;
    public final String state;

    Manifest(String videoId, String path, String state) {
        this.videoId = videoId;
        this.path = path;
        this.state = state;
    }
}
