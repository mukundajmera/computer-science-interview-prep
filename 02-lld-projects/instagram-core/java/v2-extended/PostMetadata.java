public class PostMetadata {
    private final String postId;
    private final String userId;
    private final String mediaKey;
    private final String caption;
    private final long timestamp;

    public PostMetadata(String postId, String userId, String mediaKey, String caption, long timestamp) {
        this.postId = postId;
        this.userId = userId;
        this.mediaKey = mediaKey;
        this.caption = caption;
        this.timestamp = timestamp;
    }

    public String getPostId() { return postId; }
    public String getUserId() { return userId; }
    public String getMediaKey() { return mediaKey; }
    public String getCaption() { return caption; }
    public long getTimestamp() { return timestamp; }
}
