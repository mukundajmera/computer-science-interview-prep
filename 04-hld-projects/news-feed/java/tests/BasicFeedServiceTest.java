import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class BasicFeedServiceTest {

    private InMemoryPostRepository postRepository;
    private InMemoryFollowRepository followRepository;
    private BasicFeedService feedService;

    @BeforeEach
    void setUp() {
        postRepository = new InMemoryPostRepository();
        followRepository = new InMemoryFollowRepository();
        feedService = new BasicFeedService(postRepository, followRepository);
    }

    @Test
    void testCreatePostAndGetFeed() throws InterruptedException {
        // User A creates posts, User B follows User A
        feedService.follow("userB", "userA");
        
        Post post1 = feedService.createPost("userA", "Hello World!");
        Thread.sleep(10); // Ensure different timestamps
        Post post2 = feedService.createPost("userA", "Second Post!");

        List<Post> feed = feedService.getFeed("userB", null, 10);
        
        assertEquals(2, feed.size());
        assertEquals(post2.getPostId(), feed.get(0).getPostId());
        assertEquals(post1.getPostId(), feed.get(1).getPostId());
    }

    @Test
    void testEmptyFeedIfNoFollowees() {
        feedService.createPost("userA", "Post A");
        // User B follows no one
        List<Post> feed = feedService.getFeed("userB", null, 10);
        assertTrue(feed.isEmpty());
    }

    @Test
    void testUnfollowRemovesPostsFromFeed() {
        feedService.follow("userB", "userA");
        feedService.createPost("userA", "Post to be removed from feed");
        
        List<Post> feedBefore = feedService.getFeed("userB", null, 10);
        assertEquals(1, feedBefore.size());

        feedService.unfollow("userB", "userA");
        
        List<Post> feedAfter = feedService.getFeed("userB", null, 10);
        assertTrue(feedAfter.isEmpty());
    }

    @Test
    void testCannotFollowYourself() {
        assertThrows(IllegalArgumentException.class, () -> {
            feedService.follow("userA", "userA");
        });
    }

    @Test
    void testCannotCreateEmptyPost() {
        assertThrows(IllegalArgumentException.class, () -> {
            feedService.createPost("userA", "");
        });
    }
}
