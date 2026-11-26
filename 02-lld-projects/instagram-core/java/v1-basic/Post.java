import java.util.concurrent.atomic.AtomicInteger;

public class Post {
    private String postId;
    private String authorId;
    private String mediaUrl;
    private String caption;
    private long timestamp;
    private AtomicInteger likeCount;

    public Post(String postId, String authorId, String mediaUrl, String caption, long timestamp) {
        this.postId = postId;
        this.authorId = authorId;
        this.mediaUrl = mediaUrl;
        this.caption = caption;
        this.timestamp = timestamp;
        this.likeCount = new AtomicInteger(0);
    }

    public String getPostId() {
        return postId;
    }

    public String getAuthorId() {
        return authorId;
    }

    public String getMediaUrl() {
        return mediaUrl;
    }

    public String getCaption() {
        return caption;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public int getLikeCount() {
        return likeCount.get();
    }

    public void incrementLikeCount() {
        this.likeCount.incrementAndGet();
    }
}
