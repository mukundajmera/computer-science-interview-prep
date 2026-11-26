/**
 * News Feed Service - V1 Basic
 * 
 * Core feed service implementation with pull-based approach.
 */

import java.time.Instant;
import java.util.*;

/**
 * Post entity.
 */
class Post {
    private final String postId;
    private final String userId;
    private final String content;
    private final Instant createdAt;
    private int likeCount;
    private int shareCount;
    
    public Post(String userId, String content) {
        this.postId = UUID.randomUUID().toString();
        this.userId = userId;
        this.content = content;
        this.createdAt = Instant.now();
        this.likeCount = 0;
        this.shareCount = 0;
    }
    
    // Getters
    public String getPostId() { return postId; }
    public String getUserId() { return userId; }
    public String getContent() { return content; }
    public Instant getCreatedAt() { return createdAt; }
    public int getLikeCount() { return likeCount; }
    public int getShareCount() { return shareCount; }
}

/**
 * Feed service interface.
 */
interface FeedService {
    /**
     * Create a new post.
     */
    Post createPost(String userId, String content);
    
    /**
     * Get home feed for a user.
     */
    List<Post> getFeed(String userId, String cursor, int limit);
    
    /**
     * Follow a user.
     */
    void follow(String followerId, String followeeId);
    
    /**
     * Unfollow a user.
     */
    void unfollow(String followerId, String followeeId);
}

/**
 * Post repository interface.
 */
interface PostRepository {
    void save(Post post);
    Optional<Post> findById(String postId);
    List<Post> findByUserIds(List<String> userIds, Instant before, int limit);
    List<Post> findByUserId(String userId, int limit);
}

/**
 * Follow graph repository interface.
 */
interface FollowRepository {
    void addFollow(String followerId, String followeeId);
    void removeFollow(String followerId, String followeeId);
    Set<String> getFollowees(String userId);
    Set<String> getFollowers(String userId);
    int getFollowerCount(String userId);
}

/**
 * Basic feed service - pull-based implementation.
 * Fetches posts from all followees on each request.
 */
class BasicFeedService implements FeedService {
    
    private final PostRepository postRepository;
    private final FollowRepository followRepository;
    
    public BasicFeedService(PostRepository postRepository, 
                           FollowRepository followRepository) {
        this.postRepository = postRepository;
        this.followRepository = followRepository;
    }
    
    @Override
    public Post createPost(String userId, String content) {
        if (content == null || content.trim().isEmpty()) {
            throw new IllegalArgumentException("Post content cannot be empty");
        }
        
        Post post = new Post(userId, content);
        postRepository.save(post);
        return post;
    }
    
    @Override
    public List<Post> getFeed(String userId, String cursor, int limit) {
        // Get all users this person follows
        Set<String> followees = followRepository.getFollowees(userId);
        
        if (followees.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Parse cursor (timestamp)
        Instant before = cursor != null ? 
            Instant.parse(cursor) : Instant.now();
        
        // Fetch posts from all followees
        List<Post> posts = postRepository.findByUserIds(
            new ArrayList<>(followees), before, limit);
        
        // Sort by created time descending
        posts.sort((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()));
        
        // Limit results
        if (posts.size() > limit) {
            posts = posts.subList(0, limit);
        }
        
        return posts;
    }
    
    @Override
    public void follow(String followerId, String followeeId) {
        if (followerId.equals(followeeId)) {
            throw new IllegalArgumentException("Cannot follow yourself");
        }
        followRepository.addFollow(followerId, followeeId);
    }
    
    @Override
    public void unfollow(String followerId, String followeeId) {
        followRepository.removeFollow(followerId, followeeId);
    }
}

/**
 * In-memory post repository.
 */
class InMemoryPostRepository implements PostRepository {
    
    private final Map<String, Post> posts = new HashMap<>();
    private final Map<String, List<Post>> userPosts = new HashMap<>();
    
    @Override
    public synchronized void save(Post post) {
        posts.put(post.getPostId(), post);
        userPosts.computeIfAbsent(post.getUserId(), k -> new ArrayList<>())
                 .add(post);
    }
    
    @Override
    public Optional<Post> findById(String postId) {
        return Optional.ofNullable(posts.get(postId));
    }
    
    @Override
    public List<Post> findByUserIds(List<String> userIds, Instant before, int limit) {
        List<Post> result = new ArrayList<>();
        
        for (String userId : userIds) {
            List<Post> userPostList = userPosts.getOrDefault(userId, Collections.emptyList());
            for (Post post : userPostList) {
                if (post.getCreatedAt().isBefore(before)) {
                    result.add(post);
                }
            }
        }
        
        result.sort((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()));
        return result.subList(0, Math.min(result.size(), limit));
    }
    
    @Override
    public List<Post> findByUserId(String userId, int limit) {
        List<Post> userPostList = userPosts.getOrDefault(userId, Collections.emptyList());
        List<Post> sorted = new ArrayList<>(userPostList);
        sorted.sort((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()));
        return sorted.subList(0, Math.min(sorted.size(), limit));
    }
}

/**
 * In-memory follow repository.
 */
class InMemoryFollowRepository implements FollowRepository {
    
    // userId -> set of users they follow
    private final Map<String, Set<String>> following = new HashMap<>();
    // userId -> set of their followers
    private final Map<String, Set<String>> followers = new HashMap<>();
    
    @Override
    public synchronized void addFollow(String followerId, String followeeId) {
        following.computeIfAbsent(followerId, k -> new HashSet<>()).add(followeeId);
        followers.computeIfAbsent(followeeId, k -> new HashSet<>()).add(followerId);
    }
    
    @Override
    public synchronized void removeFollow(String followerId, String followeeId) {
        Set<String> followees = following.get(followerId);
        if (followees != null) {
            followees.remove(followeeId);
        }
        
        Set<String> followerSet = followers.get(followeeId);
        if (followerSet != null) {
            followerSet.remove(followerId);
        }
    }
    
    @Override
    public Set<String> getFollowees(String userId) {
        return new HashSet<>(following.getOrDefault(userId, Collections.emptySet()));
    }
    
    @Override
    public Set<String> getFollowers(String userId) {
        return new HashSet<>(followers.getOrDefault(userId, Collections.emptySet()));
    }
    
    @Override
    public int getFollowerCount(String userId) {
        return followers.getOrDefault(userId, Collections.emptySet()).size();
    }
}
