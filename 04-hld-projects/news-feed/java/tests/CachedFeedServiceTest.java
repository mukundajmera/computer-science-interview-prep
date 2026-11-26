import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

public class CachedFeedServiceTest {

    private InMemoryPostRepository postRepository;
    private InMemoryFollowRepository followRepository;
    private InMemoryFeedCache feedCache;
    private InMemoryFanoutQueue fanoutQueue;
    private CachedFeedService feedService;

    @BeforeEach
    void setUp() {
        postRepository = new InMemoryPostRepository();
        followRepository = new InMemoryFollowRepository();
        feedCache = new InMemoryFeedCache();
        fanoutQueue = new InMemoryFanoutQueue();
        feedService = new CachedFeedService(postRepository, followRepository, feedCache, fanoutQueue, 2);
    }

    @AfterEach
    void tearDown() {
        if (feedService != null) {
            feedService.shutdown();
        }
    }

    @Test
    void testFanoutForRegularUser() throws InterruptedException {
        feedService.follow("userB", "userA");
        feedService.follow("userC", "userA");
        
        Post post = feedService.createPost("userA", "Hello Regular World!");
        
        // Wait for fanout processing
        Thread.sleep(100);
        
        List<Post> feedB = feedService.getFeed("userB", null, 10);
        assertEquals(1, feedB.size());
        assertEquals(post.getPostId(), feedB.get(0).getPostId());
        
        List<Post> feedC = feedService.getFeed("userC", null, 10);
        assertEquals(1, feedC.size());
    }

    @Test
    void testNoFanoutForCelebrity() throws InterruptedException {
        // Make userA a celebrity
        for (int i = 0; i < 10001; i++) {
            followRepository.addFollow("user_" + i, "userA");
        }
        
        feedService.follow("userB", "userA"); // ensure userB follows
        
        Post post = feedService.createPost("userA", "Hello Celebrity World!");
        
        // Ensure fanout does not put it in userB's cache
        Thread.sleep(100);
        List<String> cachedFeed = feedCache.getFeed("userB", System.currentTimeMillis() + 10000, 10);
        assertTrue(cachedFeed.isEmpty());
        
        // However, getFeed should fetch it dynamically
        List<Post> feed = feedService.getFeed("userB", null, 10);
        assertEquals(1, feed.size());
        assertEquals(post.getPostId(), feed.get(0).getPostId());
    }

    @Test
    void testGetFeedCombinesCachedAndCelebrity() throws InterruptedException {
        // userC is regular
        feedService.follow("userB", "userC");
        feedService.createPost("userC", "Regular post");
        
        // userA is celebrity
        for (int i = 0; i < 10001; i++) {
            followRepository.addFollow("user_" + i, "userA");
        }
        feedService.follow("userB", "userA");
        feedService.createPost("userA", "Celebrity post");
        
        Thread.sleep(100);
        
        List<Post> feed = feedService.getFeed("userB", null, 10);
        assertEquals(2, feed.size());
    }
}
