
public class VideoViewEvent {
    private final String videoId;
    private final String userId;
    private final long timestamp;

    public VideoViewEvent(String videoId, String userId, long timestamp) {
        this.videoId = videoId;
        this.userId = userId;
        this.timestamp = timestamp;
    }

    public String getVideoId() {
        return videoId;
    }

    public String getUserId() {
        return userId;
    }

    public long getTimestamp() {
        return timestamp;
    }
}
