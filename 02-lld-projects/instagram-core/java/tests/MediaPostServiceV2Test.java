import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;

public class MediaPostServiceV2Test {

    private FollowGraphService followGraph;
    private MediaStorageGateway storage;
    private MediaPostServiceV2 postService;
    private FeedComposer composer;

    @BeforeEach
    void setUp() {
        followGraph = new FollowGraphService(2); // threshold = 2
        storage = new MediaStorageGateway();
        postService = new MediaPostServiceV2(followGraph, storage);
        composer = new FeedComposer(postService, followGraph);
    }

    @Test
    void testStandardFanOutOnWrite() {
        followGraph.follow("u1", "u2");
        postService.createPost("u2", "imgbytes", "caption2");
        List<PostMetadata> feed = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed.size());
        Assertions.assertEquals("u2", feed.get(0).getUserId());
        Assertions.assertEquals("caption2", feed.get(0).getCaption());
    }

    @Test
    void testCelebrityFanOutOnRead() {
        followGraph.follow("u1", "celeb");
        followGraph.follow("u2", "celeb");

        postService.createPost("celeb", "celebimg", "celebcap");

        List<PostMetadata> feed1 = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed1.size());
        Assertions.assertEquals("celeb", feed1.get(0).getUserId());

        List<PostMetadata> pushFeed = postService.getUserFeed("u1");
        Assertions.assertTrue(pushFeed.isEmpty());
    }

    @Test
    void testPagination() throws InterruptedException {
        followGraph.follow("u1", "u2");
        postService.createPost("u2", "img1", "c1");
        
        postService.createPost("u2", "img2", "c2");
        
        postService.createPost("u2", "img3", "c3");

        List<PostMetadata> page1 = composer.composeFeed("u1", null, 2);
        Assertions.assertEquals(2, page1.size());
        Assertions.assertEquals("c3", page1.get(0).getCaption());
        Assertions.assertEquals("c2", page1.get(1).getCaption());

        String cursor = page1.get(1).getTimestamp() + "_" + page1.get(1).getPostId();
        List<PostMetadata> page2 = composer.composeFeed("u1", cursor, 2);
        Assertions.assertEquals(1, page2.size());
        Assertions.assertEquals("c1", page2.get(0).getCaption());
    }

    @Test
    void testRollbackOnFanoutFailure() {
        FollowGraphService mockGraph = new FollowGraphService(2) {
            @Override
            public boolean isCelebrity(String userId) {
                return false; // trigger fanout
            }
            @Override
            public java.util.Set<String> getFollowers(String userId) {
                throw new RuntimeException("Simulated fanout failure");
            }
        };
        MediaPostServiceV2 service = new MediaPostServiceV2(mockGraph, storage);
        
        try {
            service.createPost("u1", "img", "cap");
            Assertions.fail("Expected exception");
        } catch (RuntimeException e) {
            Assertions.assertEquals("Simulated fanout failure", e.getMessage());
        }
        
        Assertions.assertTrue(service.getAllPosts().isEmpty(), "Post should be rolled back");
    }

    @Test
    void testUnfollowRemovesPosts() {
        followGraph.follow("u1", "u2");
        postService.createPost("u2", "imgbytes", "caption2");
        List<PostMetadata> feed = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed.size());

        followGraph.unfollow("u1", "u2");
        List<PostMetadata> feed2 = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(0, feed2.size());
    }

    @Test
    void testDeletePost() {
        followGraph.follow("u1", "u2");
        String postId = postService.createPost("u2", "img", "caption2");
        List<PostMetadata> feed = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed.size());

        postService.deletePost(postId);
        List<PostMetadata> feed2 = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(0, feed2.size());
    }

    @Test
    void testPrivacy() {
        followGraph.follow("u1", "u3");
        postService.createPost("u3", "img", "pub");
        Assertions.assertEquals(1, composer.composeFeed("u1", null, 10).size());

        followGraph.setPrivacy("u3", true);
        Assertions.assertEquals(1, composer.composeFeed("u1", null, 10).size());

        followGraph.follow("u4", "u3");
        postService.createPost("u3", "img", "pub2");
        Assertions.assertEquals(2, composer.composeFeed("u4", null, 10).size());

        followGraph.unfollow("u4", "u3");
        Assertions.assertEquals(0, composer.composeFeed("u4", null, 10).size());

        followGraph.follow("u1", "celeb2");
        followGraph.follow("u2", "celeb2");
        postService.createPost("celeb2", "img", "c_post");
        Assertions.assertEquals(2, composer.composeFeed("u1", null, 10).size());

        followGraph.setPrivacy("celeb2", true);
        Assertions.assertEquals(2, composer.composeFeed("u1", null, 10).size());

        followGraph.unfollow("u1", "celeb2");
        Assertions.assertEquals(1, composer.composeFeed("u1", null, 10).size());
    }
}
