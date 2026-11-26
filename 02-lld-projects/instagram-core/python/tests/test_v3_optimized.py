import os
import sys
import unittest

BASE_DIR = os.path.dirname(__file__)
V3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v3-optimized"))
if V3_DIR not in sys.path:
    sys.path.insert(0, V3_DIR)

from media_post_service_v3 import MediaPostServiceV3, DistributedRepository, IdempotencyStore
from follow_graph_service_v3 import FollowGraphServiceV3
from feed_composer_v3 import FeedComposerV3

class TestInstagramV3(unittest.TestCase):
    def setUp(self):
        self.repo = DistributedRepository()
        self.idemp = IdempotencyStore()
        self.follow_graph = FollowGraphServiceV3(celebrity_threshold=2)
        self.service = MediaPostServiceV3(self.repo, self.idemp, self.follow_graph)
        self.composer = FeedComposerV3(self.service, self.follow_graph)

    def test_idempotent_upsert(self):
        success1 = self.service.upsert("p1", "u1", "m1", "cap1", "idemp1", "us-east")
        self.assertTrue(success1)
        
        # same idempotency key
        success2 = self.service.upsert("p1", "u1", "m1", "cap1", "idemp1", "us-east")
        self.assertFalse(success2)

        # different idempotency key
        success3 = self.service.upsert("p2", "u1", "m2", "cap2", "idemp2", "us-east")
        self.assertTrue(success3)

    def test_regional_fetch(self):
        self.service.upsert("p1", "u1", "m1", "cap1", "idemp1", "us-east")
        
        post = self.service.get("p1", "us-east")
        self.assertIsNotNone(post)
        self.assertEqual(post.caption, "cap1")
        
        # Wrong region
        post2 = self.service.get("p1", "eu-west")
        self.assertIsNone(post2)

    def test_standard_fan_out_on_write(self):
        self.follow_graph.follow("u1", "u2")
        self.service.upsert("p1", "u2", "img", "caption2", "i1", "us-east")
        feed = self.composer.compose_feed("u1")
        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0].user_id, "u2")
        self.assertEqual(feed[0].caption, "caption2")

    def test_celebrity_fan_out_on_read(self):
        # make celeb a celebrity (threshold = 2)
        self.follow_graph.follow("u1", "celeb")
        self.follow_graph.follow("u2", "celeb")
        
        self.service.upsert("p1", "celeb", "celeb_img", "celeb_cap", "i1", "us-east")
        
        feed1 = self.composer.compose_feed("u1")
        self.assertEqual(len(feed1), 1)
        self.assertEqual(feed1[0].user_id, "celeb")
        
        # celeb's posts shouldn't be in u1's pre-computed push feed
        self.assertNotIn("celeb", [p.user_id for p in self.service.get_user_feed("u1")])

    def test_pagination(self):
        self.follow_graph.follow("u1", "u2")
        self.service.upsert("p1", "u2", "img1", "c1", "i1", "us-east")
        self.service.upsert("p2", "u2", "img2", "c2", "i2", "us-east")
        self.service.upsert("p3", "u2", "img3", "c3", "i3", "us-east")
        
        feed_page1 = self.composer.compose_feed("u1", limit=2)
        self.assertEqual(len(feed_page1), 2)
        self.assertEqual(feed_page1[0].caption, "c3")
        self.assertEqual(feed_page1[1].caption, "c2")
        
        cursor = f"{feed_page1[-1].timestamp}_{feed_page1[-1].post_id}"
        feed_page2 = self.composer.compose_feed("u1", cursor=cursor, limit=2)
        self.assertEqual(len(feed_page2), 1)
        self.assertEqual(feed_page2[0].caption, "c1")

    def test_rollback_on_fanout_failure(self):
        class MockFollowGraph(FollowGraphServiceV3):
            def is_celebrity(self, user_id):
                return False # trigger fanout
            def get_followers(self, user_id):
                raise RuntimeError("Simulated fanout failure")
                
        mock_graph = MockFollowGraph(2)
        service = MediaPostServiceV3(self.repo, self.idemp, mock_graph)
        
        with self.assertRaises(RuntimeError) as context:
            service.upsert("p1", "u1", "img", "cap", "i1", "us-east")
            
        self.assertEqual(str(context.exception), "Simulated fanout failure")
        self.assertEqual(len(service.get_all_posts()), 0, "Post should be rolled back")
        
    def test_unfollow_removes_posts(self):
        self.follow_graph.follow("u1", "u2")
        self.service.upsert("p1", "u2", "img", "caption2", "i1", "us-east")
        feed = self.composer.compose_feed("u1")
        self.assertEqual(len(feed), 1)
        
        self.follow_graph.unfollow("u1", "u2")
        feed2 = self.composer.compose_feed("u1")
        self.assertEqual(len(feed2), 0)

    def test_delete_post(self):
        self.follow_graph.follow("u1", "u2")
        self.service.upsert("p1", "u2", "img", "caption2", "i1", "us-east")
        feed = self.composer.compose_feed("u1")
        self.assertEqual(len(feed), 1)
        
        self.service.delete_post("p1")
        feed2 = self.composer.compose_feed("u1")
        self.assertEqual(len(feed2), 0)

    def test_privacy(self):
        # u3 is public, u1 follows u3
        self.follow_graph.follow("u1", "u3")
        self.service.upsert("p1", "u3", "img", "pub", "i1", "us-east")
        self.assertEqual(len(self.composer.compose_feed("u1")), 1)
        
        # u3 goes private
        self.follow_graph.set_privacy("u3", True)
        # u1 is still a follower, should see it
        self.assertEqual(len(self.composer.compose_feed("u1")), 1)
        
        # u4 doesn't follow u3
        self.follow_graph.follow("u4", "u3")
        self.service.upsert("p2", "u3", "img", "pub2", "i2", "us-east")
        self.assertEqual(len(self.composer.compose_feed("u4")), 2)
        
        self.follow_graph.unfollow("u4", "u3")
        self.assertEqual(len(self.composer.compose_feed("u4")), 0)
        
        # Test celebrity privacy
        self.follow_graph.follow("u1", "celeb2")
        self.follow_graph.follow("u2", "celeb2") # celebrity threshold = 2
        self.service.upsert("p3", "celeb2", "img", "c_post", "i3", "us-east")
        self.assertEqual(len(self.composer.compose_feed("u1")), 2) # pub, c_post
        
        self.follow_graph.set_privacy("celeb2", True)
        self.assertEqual(len(self.composer.compose_feed("u1")), 2)
        
        self.follow_graph.unfollow("u1", "celeb2")
        self.assertEqual(len(self.composer.compose_feed("u1")), 1) # back to just pub

if __name__ == "__main__":
    unittest.main()
