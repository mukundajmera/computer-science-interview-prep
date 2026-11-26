public class PostMetadataV3 {
    private final String postId;
    private final String userId;
    private final String mediaKey;
    private final String caption;
    private final String region;
    private final long timestamp;

    public PostMetadataV3(String postId, String userId, String mediaKey, String caption, String region, long timestamp) {
        this.postId = postId;
        this.userId = userId;
        this.mediaKey = mediaKey;
        this.caption = caption;
        this.region = region;
        this.timestamp = timestamp;
    }

    public String getPostId() { return postId; }
    public String getUserId() { return userId; }
    public String getMediaKey() { return mediaKey; }
    public String getCaption() { return caption; }
    public String getRegion() { return region; }
    public long getTimestamp() { return timestamp; }
}
