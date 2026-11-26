import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedFeedServiceTest {

    private InMemoryPostRepository postRepository;
    private InMemoryFollowRepository followRepository;
    private InMemoryFeedCache feedCache;
    private EngagementRanker feedRanker;
    private DistributedFeedService feedService;

    @BeforeEach
    void setUp() {
        postRepository = new InMemoryPostRepository();
        followRepository = new InMemoryFollowRepository();
        feedCache = new InMemoryFeedCache();
        feedRanker = new EngagementRanker();
        feedService = new DistributedFeedService(postRepository, followRepository, feedCache, feedRanker);
    }

    @AfterEach
    void tearDown() {
        if (feedService != null) {
            feedService.shutdown();
        }
    }

    @Test
    void testHybridFanoutForRegularUser() throws InterruptedException {
        feedService.follow("userB", "userA");
        Post post = feedService.createPost("userA", "Post A");
        
        Thread.sleep(100);
        
        List<Post> feed = feedService.getFeed("userB", null, 10);
        assertEquals(1, feed.size());
        assertEquals(post.getPostId(), feed.get(0).getPostId());
    }

    @Test
    void testHybridFanoutForCelebrity() throws InterruptedException {
        // userA becomes a celebrity
        for (int i = 0; i < 10001; i++) {
            followRepository.addFollow("user_" + i, "userA");
        }
        
        Post post = feedService.createPost("userA", "Celeb Post");
        Thread.sleep(100);
        
        // user_0 follows userA, get feed fetches it
        List<Post> feed = feedService.getFeed("user_0", null, 10);
        assertEquals(1, feed.size());
        assertEquals(post.getPostId(), feed.get(0).getPostId());
    }

    @Test
    void testFeedRanking() throws InterruptedException {
        feedService.follow("userB", "userA");
        
        // Post 1: old, low engagement
        Post post1 = feedService.createPost("userA", "Post 1");
        
        Thread.sleep(10);
        
        // Post 2: new, but let's say it will be treated normally.
        Post post2 = feedService.createPost("userA", "Post 2");
        
        Thread.sleep(100);
        
        List<Post> feed = feedService.getFeed("userB", null, 10);
        assertEquals(2, feed.size());
        
        // Since recency is king and engagement is 0, newest should be first
        assertEquals(post2.getPostId(), feed.get(0).getPostId());
        assertEquals(post1.getPostId(), feed.get(1).getPostId());
    }
}
