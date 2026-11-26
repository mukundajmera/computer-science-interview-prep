import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;

public class MediaPostServiceTest {

    private MediaPostService service;

    @BeforeEach
    void setUp() {
        service = new MediaPostService();
    }

    @Test
    void testPostCreation() {
        Post post = service.createPost("user1", "url1", "caption1");
        Assertions.assertNotNull(post);
        Assertions.assertEquals("user1", post.getAuthorId());
        Assertions.assertEquals("url1", post.getMediaUrl());
        Assertions.assertEquals("caption1", post.getCaption());
        Assertions.assertEquals(0, post.getLikeCount());
    }

    @Test
    void testSocialGraphFollowUnfollow() {
        service.createPost("user2", "url2", "caption2");
        
        service.follow("user1", "user2");
        List<Post> feed = service.getNewsFeed("user1", 10);
        Assertions.assertEquals(1, feed.size());
        Assertions.assertEquals("user2", feed.get(0).getAuthorId());
        
        service.unfollow("user1", "user2");
        List<Post> newFeed = service.getNewsFeed("user1", 10);
        Assertions.assertEquals(0, newFeed.size());
    }

    @Test
    void testNewsFeedGenerationFromMultipleFollowees() throws InterruptedException {
        service.createPost("user2", "url2", "caption2");
        Thread.sleep(10); // Ensure timestamp difference
        service.createPost("user3", "url3", "caption3");
        Thread.sleep(10);
        service.createPost("user1", "url1", "caption1");
        
        service.follow("user1", "user2");
        service.follow("user1", "user3");
        
        List<Post> feed = service.getNewsFeed("user1", 10);
        
        Assertions.assertEquals(3, feed.size());
        Assertions.assertEquals("user1", feed.get(0).getAuthorId());
        Assertions.assertEquals("user3", feed.get(1).getAuthorId());
        Assertions.assertEquals("user2", feed.get(2).getAuthorId());
        
        List<Post> limitedFeed = service.getNewsFeed("user1", 2);
        Assertions.assertEquals(2, limitedFeed.size());
    }

    @Test
    void testLikeIncrements() {
        Post post = service.createPost("user1", "url1", "caption1");
        service.likePost(post.getPostId(), "user2");
        service.likePost(post.getPostId(), "user3");
        
        Assertions.assertEquals(2, post.getLikeCount());
    }

    @Test
    void testEmptyFeedBehavior() {
        List<Post> feed = service.getNewsFeed("user1", 10);
        Assertions.assertTrue(feed.isEmpty());
        
        service.follow("user1", "user2");
        List<Post> feedAfterFollow = service.getNewsFeed("user1", 10);
        Assertions.assertTrue(feedAfterFollow.isEmpty());
    }
}
