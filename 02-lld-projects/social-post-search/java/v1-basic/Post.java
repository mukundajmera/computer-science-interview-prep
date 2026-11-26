package v1_basic;

import java.util.List;

public class Post {
    private String postId;
    private String authorId;
    private String content;
    private List<String> tags;
    private long timestamp;

    public Post(String postId, String authorId, String content, List<String> tags, long timestamp) {
        this.postId = postId;
        this.authorId = authorId;
        this.content = content;
        this.tags = tags;
        this.timestamp = timestamp;
    }

    public String getPostId() {
        return postId;
    }

    public String getAuthorId() {
        return authorId;
    }

    public String getContent() {
        return content;
    }

    public List<String> getTags() {
        return tags;
    }

    public long getTimestamp() {
        return timestamp;
    }
}