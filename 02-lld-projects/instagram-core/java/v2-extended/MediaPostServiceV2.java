import java.util.UUID;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

public class MediaPostServiceV2 {
    private final FollowGraphService followGraph;
    private final MediaStorageGateway storage;
    
    private final Map<String, PostMetadata> posts = new ConcurrentHashMap<>();
    private final Map<String, List<PostMetadata>> userFeeds = new ConcurrentHashMap<>();
    private final AtomicLong clock = new AtomicLong(1);

    public MediaPostServiceV2(FollowGraphService followGraph, MediaStorageGateway storage) {
        this.followGraph = followGraph;
        this.storage = storage;
    }

    public String createPost(String userId, String mediaBytesRef, String caption) {
        String mediaKey = storage.put(mediaBytesRef);
        String postId = UUID.randomUUID().toString();
        PostMetadata post = new PostMetadata(postId, userId, mediaKey, caption, clock.getAndIncrement());
        posts.put(postId, post);

        try {
            if (!followGraph.isCelebrity(userId)) {
                for (String follower : followGraph.getFollowers(userId)) {
                    userFeeds.computeIfAbsent(follower, k -> new CopyOnWriteArrayList<>()).add(post);
                }
            }

            userFeeds.computeIfAbsent(userId, k -> new CopyOnWriteArrayList<>()).add(post);
        } catch (Exception e) {
            // rollback
            posts.remove(postId);
            for (List<PostMetadata> feed : userFeeds.values()) {
                feed.remove(post);
            }
            throw e;
        }

        return postId;
    }

    public Optional<PostMetadata> getPost(String postId) {
        return Optional.ofNullable(posts.get(postId));
    }
    
    public Map<String, PostMetadata> getAllPosts() {
        return Collections.unmodifiableMap(posts);
    }
    
    public List<PostMetadata> getUserFeed(String userId) {
        return userFeeds.getOrDefault(userId, Collections.emptyList());
    }

    public void deletePost(String postId) {
        PostMetadata post = posts.remove(postId);
        if (post != null) {
            for (List<PostMetadata> feed : userFeeds.values()) {
                feed.remove(post);
            }
        }
    }
}
