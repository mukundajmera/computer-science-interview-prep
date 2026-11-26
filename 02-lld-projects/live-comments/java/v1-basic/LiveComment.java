package v1_basic;

public class LiveComment {
    private final String commentId;
    private final String videoId;
    private final String userId;
    private final String message;
    private final long timestamp;
    private final long sequenceNumber;

    public LiveComment(String commentId, String videoId, String userId, String message, long timestamp, long sequenceNumber) {
        this.commentId = commentId;
        this.videoId = videoId;
        this.userId = userId;
        this.message = message;
        this.timestamp = timestamp;
        this.sequenceNumber = sequenceNumber;
    }

    public String getCommentId() {
        return commentId;
    }

    public String getVideoId() {
        return videoId;
    }

    public String getUserId() {
        return userId;
    }

    public String getMessage() {
        return message;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public long getSequenceNumber() {
        return sequenceNumber;
    }
}
