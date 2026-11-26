import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Optional;
import java.util.List;

public class MediaPostServiceV3Test {
    
    private DistributedRepository repository;
    private IdempotencyStore idempotencyStore;
    private FollowGraphServiceV3 followGraph;
    private MediaPostServiceV3 service;
    private FeedComposerV3 composer;

    @BeforeEach
    void setUp() {
        repository = new DistributedRepository();
        idempotencyStore = new IdempotencyStore();
        followGraph = new FollowGraphServiceV3(2); // threshold = 2
        service = new MediaPostServiceV3(repository, idempotencyStore, followGraph);
        composer = new FeedComposerV3(service, followGraph);
    }

    @Test
    void testIdempotentUpsert() {
        boolean success1 = service.upsert("p1", "u1", "m1", "cap1", "idemp1", "us-east");
        Assertions.assertTrue(success1);
        
        boolean success2 = service.upsert("p1", "u1", "m1", "cap1", "idemp1", "us-east");
        Assertions.assertFalse(success2);
        
        boolean success3 = service.upsert("p2", "u1", "m2", "cap2", "idemp2", "us-east");
        Assertions.assertTrue(success3);
    }

    @Test
    void testRegionalFetch() {
        service.upsert("p1", "u1", "m1", "cap1", "idemp1", "us-east");
        
        Optional<PostMetadataV3> post = service.get("p1", "us-east");
        Assertions.assertTrue(post.isPresent());
        Assertions.assertEquals("cap1", post.get().getCaption());
        
        Optional<PostMetadataV3> post2 = service.get("p1", "eu-west");
        Assertions.assertFalse(post2.isPresent());
    }

    @Test
    void testStandardFanOutOnWrite() {
        followGraph.follow("u1", "u2");
        service.upsert("p1", "u2", "imgbytes", "caption2", "idemp1", "us-east");
        List<PostMetadataV3> feed = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed.size());
        Assertions.assertEquals("u2", feed.get(0).getUserId());
        Assertions.assertEquals("caption2", feed.get(0).getCaption());
    }

    @Test
    void testCelebrityFanOutOnRead() {
        followGraph.follow("u1", "celeb");
        followGraph.follow("u2", "celeb");

        service.upsert("p1", "celeb", "celebimg", "celebcap", "idemp1", "us-east");

        List<PostMetadataV3> feed1 = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed1.size());
        Assertions.assertEquals("celeb", feed1.get(0).getUserId());

        List<PostMetadataV3> pushFeed = service.getUserFeed("u1");
        Assertions.assertTrue(pushFeed.isEmpty());
    }

    @Test
    void testPagination() throws InterruptedException {
        followGraph.follow("u1", "u2");
        service.upsert("p1", "u2", "img1", "c1", "i1", "us-east");
        service.upsert("p2", "u2", "img2", "c2", "i2", "us-east");
        service.upsert("p3", "u2", "img3", "c3", "i3", "us-east");

        List<PostMetadataV3> page1 = composer.composeFeed("u1", null, 2);
        Assertions.assertEquals(2, page1.size());
        Assertions.assertEquals("c3", page1.get(0).getCaption());
        Assertions.assertEquals("c2", page1.get(1).getCaption());

        String cursor = page1.get(1).getTimestamp() + "_" + page1.get(1).getPostId();
        List<PostMetadataV3> page2 = composer.composeFeed("u1", cursor, 2);
        Assertions.assertEquals(1, page2.size());
        Assertions.assertEquals("c1", page2.get(0).getCaption());
    }

    @Test
    void testRollbackOnFanoutFailure() {
        FollowGraphServiceV3 mockGraph = new FollowGraphServiceV3(2) {
            @Override
            public boolean isCelebrity(String userId) {
                return false; // trigger fanout
            }
            @Override
            public java.util.Set<String> getFollowers(String userId) {
                throw new RuntimeException("Simulated fanout failure");
            }
        };
        MediaPostServiceV3 faultService = new MediaPostServiceV3(repository, idempotencyStore, mockGraph);
        
        try {
            faultService.upsert("p1", "u1", "img", "cap", "i1", "us-east");
            Assertions.fail("Expected exception");
        } catch (RuntimeException e) {
            Assertions.assertEquals("Simulated fanout failure", e.getMessage());
        }
        
        Assertions.assertTrue(faultService.getAllPosts().isEmpty(), "Post should be rolled back");
    }

    @Test
    void testUnfollowRemovesPosts() {
        followGraph.follow("u1", "u2");
        service.upsert("p1", "u2", "imgbytes", "caption2", "i1", "us-east");
        List<PostMetadataV3> feed = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed.size());

        followGraph.unfollow("u1", "u2");
        List<PostMetadataV3> feed2 = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(0, feed2.size());
    }

    @Test
    void testDeletePost() {
        followGraph.follow("u1", "u2");
        service.upsert("p1", "u2", "img", "caption2", "i1", "us-east");
        List<PostMetadataV3> feed = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(1, feed.size());

        service.deletePost("p1");
        List<PostMetadataV3> feed2 = composer.composeFeed("u1", null, 10);
        Assertions.assertEquals(0, feed2.size());
    }

    @Test
    void testPrivacy() {
        followGraph.follow("u1", "u3");
        service.upsert("p1", "u3", "img", "pub", "i1", "us-east");
        Assertions.assertEquals(1, composer.composeFeed("u1", null, 10).size());

        followGraph.setPrivacy("u3", true);
        Assertions.assertEquals(1, composer.composeFeed("u1", null, 10).size());

        followGraph.follow("u4", "u3");
        service.upsert("p2", "u3", "img", "pub2", "i2", "us-east");
        Assertions.assertEquals(2, composer.composeFeed("u4", null, 10).size());

        followGraph.unfollow("u4", "u3");
        Assertions.assertEquals(0, composer.composeFeed("u4", null, 10).size());

        followGraph.follow("u1", "celeb2");
        followGraph.follow("u2", "celeb2");
        service.upsert("p3", "celeb2", "img", "c_post", "i3", "us-east");
        Assertions.assertEquals(2, composer.composeFeed("u1", null, 10).size());

        followGraph.setPrivacy("celeb2", true);
        Assertions.assertEquals(2, composer.composeFeed("u1", null, 10).size());

        followGraph.unfollow("u1", "celeb2");
        Assertions.assertEquals(1, composer.composeFeed("u1", null, 10).size());
    }
}
