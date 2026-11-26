/**
 * News Feed Service - V3 Distributed
 * 
 * Hybrid fan-out with ranking and multi-region support.
 */

import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;

/**
 * Feed ranking service interface.
 */
interface FeedRanker {
    /**
     * Rank posts for a user's feed.
     */
    List<RankedPost> rank(String userId, List<Post> posts);
}

class RankedPost {
    private final Post post;
    private final double score;
    
    public RankedPost(Post post, double score) {
        this.post = post;
        this.score = score;
    }
    
    public Post getPost() { return post; }
    public double getScore() { return score; }
}

/**
 * Simple chronological + engagement ranker.
 */
class EngagementRanker implements FeedRanker {
    
    @Override
    public List<RankedPost> rank(String userId, List<Post> posts) {
        List<RankedPost> ranked = new ArrayList<>();
        
        for (Post post : posts) {
            double score = calculateScore(post);
            ranked.add(new RankedPost(post, score));
        }
        
        // Sort by score descending
        ranked.sort((a, b) -> Double.compare(b.getScore(), a.getScore()));
        return ranked;
    }
    
    private double calculateScore(Post post) {
        // Base score from recency (hours since post)
        long ageHours = (System.currentTimeMillis() - 
                        post.getCreatedAt().toEpochMilli()) / 3600000;
        double recencyScore = Math.max(0, 100 - ageHours);
        
        // Engagement boost
        double engagementScore = Math.log10(1 + post.getLikeCount() + 
                                           post.getShareCount() * 2);
        
        return recencyScore + engagementScore * 10;
    }
}

/**
 * Distributed feed service with hybrid fan-out and ranking.
 */
class DistributedFeedService implements FeedService {
    
    private static final int CELEBRITY_THRESHOLD = 10000;
    private static final int MAX_FEED_SIZE = 1000;
    private static final int BATCH_SIZE = 100;
    
    private final PostRepository postRepository;
    private final FollowRepository followRepository;
    private final FeedCache feedCache;
    private final FeedRanker feedRanker;
    private final ExecutorService fanoutExecutor;
    
    public DistributedFeedService(PostRepository postRepository,
                                  FollowRepository followRepository,
                                  FeedCache feedCache,
                                  FeedRanker feedRanker) {
        this.postRepository = postRepository;
        this.followRepository = followRepository;
        this.feedCache = feedCache;
        this.feedRanker = feedRanker;
        this.fanoutExecutor = Executors.newFixedThreadPool(8);
    }
    
    @Override
    public Post createPost(String userId, String content) {
        Post post = new Post(userId, content);
        postRepository.save(post);
        
        // Async hybrid fan-out
        fanoutExecutor.submit(() -> hybridFanout(post, userId));
        
        return post;
    }
    
    /**
     * Hybrid fan-out strategy.
     */
    private void hybridFanout(Post post, String authorId) {
        Set<String> followers = followRepository.getFollowers(authorId);
        int followerCount = followers.size();
        
        if (followerCount < CELEBRITY_THRESHOLD) {
            // Fan-out on write for regular users
            fanoutToFollowers(post, followers);
        } else {
            // For celebrities, only fan-out to "super fans"
            // (users who interact frequently)
            Set<String> superFans = getTopEngagedFollowers(authorId, 1000);
            fanoutToFollowers(post, superFans);
        }
    }
    
    private void fanoutToFollowers(Post post, Set<String> followers) {
        long score = post.getCreatedAt().toEpochMilli();
        
        List<String> followerList = new ArrayList<>(followers);
        for (int i = 0; i < followerList.size(); i += BATCH_SIZE) {
            int end = Math.min(i + BATCH_SIZE, followerList.size());
            List<String> batch = followerList.subList(i, end);
            
            for (String followerId : batch) {
                feedCache.addToFeed(followerId, post.getPostId(), score);
            }
        }
    }
    
    private Set<String> getTopEngagedFollowers(String userId, int limit) {
        // In production: Use engagement data to find most active followers
        Set<String> allFollowers = followRepository.getFollowers(userId);
        if (allFollowers.size() <= limit) {
            return allFollowers;
        }
        
        // Return first N for simplicity
        Set<String> result = new HashSet<>();
        int count = 0;
        for (String follower : allFollowers) {
            result.add(follower);
            if (++count >= limit) break;
        }
        return result;
    }
    
    @Override
    public List<Post> getFeed(String userId, String cursor, int limit) {
        long maxScore = cursor != null ? 
            Long.parseLong(cursor) : System.currentTimeMillis();
        
        // Get pre-computed feed
        List<String> cachedPostIds = feedCache.getFeed(userId, maxScore, limit * 2);
        
        // Get celebrity posts
        Set<String> followees = followRepository.getFollowees(userId);
        List<Post> celebrityPosts = fetchCelebrityPosts(followees, maxScore, limit);
        
        // Hydrate cached posts
        List<Post> cachedPosts = new ArrayList<>();
        for (String postId : cachedPostIds) {
            postRepository.findById(postId).ifPresent(cachedPosts::add);
        }
        
        // Merge all posts
        Set<String> seen = new HashSet<>();
        List<Post> allPosts = new ArrayList<>();
        
        for (Post post : cachedPosts) {
            if (seen.add(post.getPostId())) {
                allPosts.add(post);
            }
        }
        for (Post post : celebrityPosts) {
            if (seen.add(post.getPostId())) {
                allPosts.add(post);
            }
        }
        
        // Rank posts
        List<RankedPost> ranked = feedRanker.rank(userId, allPosts);
        
        // Return top N
        List<Post> result = new ArrayList<>();
        for (int i = 0; i < Math.min(limit, ranked.size()); i++) {
            result.add(ranked.get(i).getPost());
        }
        
        return result;
    }
    
    private List<Post> fetchCelebrityPosts(Set<String> followees, 
                                           long maxScore, int limit) {
        List<String> celebrities = new ArrayList<>();
        
        for (String followee : followees) {
            if (followRepository.getFollowerCount(followee) >= CELEBRITY_THRESHOLD) {
                celebrities.add(followee);
            }
        }
        
        if (celebrities.isEmpty()) {
            return Collections.emptyList();
        }
        
        Instant before = Instant.ofEpochMilli(maxScore);
        return postRepository.findByUserIds(celebrities, before, limit);
    }
    
    @Override
    public void follow(String followerId, String followeeId) {
        followRepository.addFollow(followerId, followeeId);
        
        // Backfill async
        fanoutExecutor.submit(() -> {
            List<Post> recentPosts = postRepository.findByUserId(followeeId, 50);
            for (Post post : recentPosts) {
                feedCache.addToFeed(followerId, post.getPostId(),
                                   post.getCreatedAt().toEpochMilli());
            }
            feedCache.trimFeed(followerId, MAX_FEED_SIZE);
        });
    }
    
    @Override
    public void unfollow(String followerId, String followeeId) {
        followRepository.removeFollow(followerId, followeeId);
    }
    
    public void shutdown() {
        fanoutExecutor.shutdown();
    }
}

// ============================================================================
// Pattern Integration Hooks (Real-time transport, contention, workflow durability)
// ============================================================================

enum DeliveryMode {
    POLLING,
    LONG_POLLING,
    SSE,
    WEBSOCKET
    // WebRTC could be used for media-heavy peer delivery when applicable.
}

enum ContentionPolicy {
    OPTIMISTIC,
    PESSIMISTIC,
    SERIAL_QUEUE,
    DISTRIBUTED_LOCK
}

class ExecutionResult {
    private final boolean success;
    private final String checkpointId;
    private final String errorMessage;
    private final boolean retryable;

    private ExecutionResult(boolean success, String checkpointId, String errorMessage, boolean retryable) {
        this.success = success;
        this.checkpointId = checkpointId;
        this.errorMessage = errorMessage;
        this.retryable = retryable;
    }

    public static ExecutionResult success(String checkpointId) {
        return new ExecutionResult(true, checkpointId, null, false);
    }

    public static ExecutionResult failure(String checkpointId, String errorMessage, boolean retryable) {
        return new ExecutionResult(false, checkpointId, errorMessage, retryable);
    }

    public boolean isSuccess() { return success; }
    public String getCheckpointId() { return checkpointId; }
    public String getErrorMessage() { return errorMessage; }
    public boolean isRetryable() { return retryable; }
}

interface WorkflowStep {
    String name();
    ExecutionResult execute();
}

interface CompensationStep {
    String name();
    void compensate(String checkpointId);
}

interface WorkflowOrchestrator {
    ExecutionResult runStep(WorkflowStep step, String idempotencyKey, IdempotencyStore store);
    void registerCompensation(String checkpointId, CompensationStep compensationStep);
}

interface IdempotencyStore {
    boolean hasProcessed(String key);
    void markProcessed(String key, ExecutionResult result);
    Optional<ExecutionResult> getResult(String key);
}
