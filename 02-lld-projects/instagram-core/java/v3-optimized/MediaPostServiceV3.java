import java.util.Optional;
import java.util.Map;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.Collections;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;

public class MediaPostServiceV3 {
    private final DistributedRepository repository;
    private final IdempotencyStore idempotencyStore;
    private final FollowGraphServiceV3 followGraph;
    
    private final Map<String, List<PostMetadataV3>> userFeeds = new ConcurrentHashMap<>();
    private final AtomicLong clock = new AtomicLong(1);

    public MediaPostServiceV3(DistributedRepository repository, IdempotencyStore idempotencyStore, FollowGraphServiceV3 followGraph) {
        this.repository = repository;
        this.idempotencyStore = idempotencyStore;
        this.followGraph = followGraph;
    }

    public boolean upsert(String postId, String userId, String mediaKey, String caption, String idempotencyKey, String region) {
        if (!idempotencyStore.claim(idempotencyKey, 60_000)) {
            return false; // Already processed
        }
        
        long timestamp = clock.getAndIncrement();
        PostMetadataV3 post = new PostMetadataV3(postId, userId, mediaKey, caption, region, timestamp);
        repository.save(postId, post, region);
        
        try {
            if (!followGraph.isCelebrity(userId)) {
                for (String follower : followGraph.getFollowers(userId)) {
                    userFeeds.computeIfAbsent(follower, k -> new CopyOnWriteArrayList<>()).add(post);
                }
            }

            userFeeds.computeIfAbsent(userId, k -> new CopyOnWriteArrayList<>()).add(post);
        } catch (Exception e) {
            // rollback
            repository.delete(postId);
            for (List<PostMetadataV3> feed : userFeeds.values()) {
                feed.remove(post);
            }
            throw e;
        }

        return true;
    }

    public Optional<PostMetadataV3> get(String key, String region) {
        return repository.find(key, region);
    }
    
    public Map<String, PostMetadataV3> getAllPosts() {
        return repository.getAllPosts();
    }
    
    public List<PostMetadataV3> getUserFeed(String userId) {
        return userFeeds.getOrDefault(userId, Collections.emptyList());
    }
    
    public void deletePost(String postId) {
        // Need region for v3 deletion typically, but assuming global delete here for parity with v2 behavior
        PostMetadataV3 post = repository.getAllPosts().get(postId);
        if (post != null) {
            repository.delete(postId);
            for (List<PostMetadataV3> feed : userFeeds.values()) {
                feed.remove(post);
            }
        }
    }
}
