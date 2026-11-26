/**
 * News Feed Service - V2 Scaled
 * 
 * Fan-out on write with Redis caching.
 */

import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;

/**
 * Feed cache interface (Redis abstraction).
 */
interface FeedCache {
    /**
     * Add post to user's feed.
     */
    void addToFeed(String userId, String postId, long score);
    
    /**
     * Get feed post IDs for a user.
     */
    List<String> getFeed(String userId, long maxScore, int limit);
    
    /**
     * Trim feed to max size.
     */
    void trimFeed(String userId, int maxSize);
}

/**
 * Message queue for fan-out processing.
 */
interface FanoutQueue {
    void publishPost(String postId, String authorId);
    FanoutMessage poll(long timeout, TimeUnit unit) throws InterruptedException;
}

class FanoutMessage {
    private final String postId;
    private final String authorId;
    
    public FanoutMessage(String postId, String authorId) {
        this.postId = postId;
        this.authorId = authorId;
    }
    
    public String getPostId() { return postId; }
    public String getAuthorId() { return authorId; }
}

/**
 * Cached feed service with fan-out on write.
 */
class CachedFeedService implements FeedService {
    
    private static final int CELEBRITY_THRESHOLD = 10000;
    private static final int MAX_FEED_SIZE = 1000;
    
    private final PostRepository postRepository;
    private final FollowRepository followRepository;
    private final FeedCache feedCache;
    private final FanoutQueue fanoutQueue;
    private final ExecutorService fanoutExecutor;
    private volatile boolean running = true;
    
    public CachedFeedService(PostRepository postRepository,
                            FollowRepository followRepository,
                            FeedCache feedCache,
                            FanoutQueue fanoutQueue,
                            int fanoutWorkers) {
        this.postRepository = postRepository;
        this.followRepository = followRepository;
        this.feedCache = feedCache;
        this.fanoutQueue = fanoutQueue;
        this.fanoutExecutor = Executors.newFixedThreadPool(fanoutWorkers);
        
        // Start fanout workers
        for (int i = 0; i < fanoutWorkers; i++) {
            fanoutExecutor.submit(this::fanoutWorker);
        }
    }
    
    @Override
    public Post createPost(String userId, String content) {
        Post post = new Post(userId, content);
        postRepository.save(post);
        
        // Check if celebrity (skip fanout for them)
        int followerCount = followRepository.getFollowerCount(userId);
        
        if (followerCount < CELEBRITY_THRESHOLD) {
            // Queue for fan-out
            fanoutQueue.publishPost(post.getPostId(), userId);
        }
        
        return post;
    }
    
    @Override
    public List<Post> getFeed(String userId, String cursor, int limit) {
        long maxScore = cursor != null ? 
            Long.parseLong(cursor) : System.currentTimeMillis();
        
        // Get pre-computed feed from cache, make mutable
        List<String> postIds = new ArrayList<>(feedCache.getFeed(userId, maxScore, limit));
        
        // Get followed celebrities and fetch their recent posts
        Set<String> followees = followRepository.getFollowees(userId);
        List<String> celebrities = new ArrayList<>();
        
        for (String followee : followees) {
            if (followRepository.getFollowerCount(followee) >= CELEBRITY_THRESHOLD) {
                celebrities.add(followee);
            }
        }
        
        // Fetch celebrity posts
        if (!celebrities.isEmpty()) {
            Instant before = Instant.ofEpochMilli(maxScore);
            List<Post> celebPosts = postRepository.findByUserIds(celebrities, before, limit);
            for (Post p : celebPosts) {
                if (!postIds.contains(p.getPostId())) {
                    postIds.add(p.getPostId());
                }
            }
        }
        
        // Hydrate posts
        List<Post> posts = new ArrayList<>();
        for (String postId : postIds) {
            postRepository.findById(postId).ifPresent(posts::add);
        }
        
        // Sort by time and limit
        posts.sort((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()));
        if (posts.size() > limit) {
            posts = posts.subList(0, limit);
        }
        
        return posts;
    }
    
    @Override
    public void follow(String followerId, String followeeId) {
        followRepository.addFollow(followerId, followeeId);
        
        // Backfill recent posts from new followee
        List<Post> recentPosts = postRepository.findByUserId(followeeId, 20);
        for (Post post : recentPosts) {
            feedCache.addToFeed(followerId, post.getPostId(), 
                               post.getCreatedAt().toEpochMilli());
        }
        feedCache.trimFeed(followerId, MAX_FEED_SIZE);
    }
    
    @Override
    public void unfollow(String followerId, String followeeId) {
        followRepository.removeFollow(followerId, followeeId);
        // Note: We don't remove posts from cache (they'll expire naturally)
    }
    
    /**
     * Fan-out worker loop.
     */
    private void fanoutWorker() {
        while (running) {
            try {
                FanoutMessage message = fanoutQueue.poll(1, TimeUnit.SECONDS);
                if (message != null) {
                    processFanout(message);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    /**
     * Process fan-out for a post.
     */
    private void processFanout(FanoutMessage message) {
        Set<String> followers = followRepository.getFollowers(message.getAuthorId());
        long score = System.currentTimeMillis();
        
        for (String followerId : followers) {
            feedCache.addToFeed(followerId, message.getPostId(), score);
            feedCache.trimFeed(followerId, MAX_FEED_SIZE);
        }
    }
    
    public void shutdown() {
        running = false;
        fanoutExecutor.shutdown();
    }
}

/**
 * In-memory feed cache (simulating Redis).
 */
class InMemoryFeedCache implements FeedCache {
    
    // userId -> TreeMap<score, postId>
    private final Map<String, TreeMap<Long, String>> feeds = new ConcurrentHashMap<>();
    
    @Override
    public void addToFeed(String userId, String postId, long score) {
        feeds.computeIfAbsent(userId, k -> new TreeMap<>(Collections.reverseOrder()))
             .put(score, postId);
    }
    
    @Override
    public List<String> getFeed(String userId, long maxScore, int limit) {
        TreeMap<Long, String> feed = feeds.get(userId);
        if (feed == null) {
            return Collections.emptyList();
        }
        
        List<String> result = new ArrayList<>();
        for (Map.Entry<Long, String> entry : feed.entrySet()) {
            if (entry.getKey() < maxScore) {
                result.add(entry.getValue());
                if (result.size() >= limit) break;
            }
        }
        return result;
    }
    
    @Override
    public synchronized void trimFeed(String userId, int maxSize) {
        TreeMap<Long, String> feed = feeds.get(userId);
        if (feed != null && feed.size() > maxSize) {
            while (feed.size() > maxSize) {
                feed.pollLastEntry();
            }
        }
    }
}

/**
 * In-memory fanout queue.
 */
class InMemoryFanoutQueue implements FanoutQueue {
    
    private final BlockingQueue<FanoutMessage> queue = new LinkedBlockingQueue<>();
    
    @Override
    public void publishPost(String postId, String authorId) {
        queue.offer(new FanoutMessage(postId, authorId));
    }
    
    @Override
    public FanoutMessage poll(long timeout, TimeUnit unit) throws InterruptedException {
        return queue.poll(timeout, unit);
    }
}
