import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.concurrent.atomic.AtomicInteger;

public class MediaPostService {
    private final Map<String, Post> posts = new ConcurrentHashMap<>();
    private final Map<String, Set<String>> following = new ConcurrentHashMap<>();
    private final AtomicInteger postCounter = new AtomicInteger(0);

    public Post createPost(String authorId, String mediaUrl, String caption) {
        String postId = "post_" + postCounter.incrementAndGet();
        Post post = new Post(postId, authorId, mediaUrl, caption, System.currentTimeMillis());
        posts.put(postId, post);
        return post;
    }

    public void follow(String followerId, String followeeId) {
        following.computeIfAbsent(followerId, k -> new CopyOnWriteArraySet<>()).add(followeeId);
    }

    public void unfollow(String followerId, String followeeId) {
        Set<String> followees = following.get(followerId);
        if (followees != null) {
            followees.remove(followeeId);
        }
    }

    public List<Post> getNewsFeed(String userId, int limit) {
        Set<String> followees = following.getOrDefault(userId, Collections.emptySet());
        List<Post> feed = new ArrayList<>();
        
        for (Post post : posts.values()) {
            if (followees.contains(post.getAuthorId()) || post.getAuthorId().equals(userId)) {
                feed.add(post);
            }
        }

        feed.sort((p1, p2) -> Long.compare(p2.getTimestamp(), p1.getTimestamp()));
        
        return feed.size() > limit ? feed.subList(0, limit) : feed;
    }

    public void likePost(String postId, String userId) {
        Post post = posts.get(postId);
        if (post != null) {
            post.incrementLikeCount();
        }
    }
}
