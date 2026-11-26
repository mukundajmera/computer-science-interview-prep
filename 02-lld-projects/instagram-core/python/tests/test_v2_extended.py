import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(__file__)
V2_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v2-extended"))
if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)

from follow_graph_service import FollowGraphService
from media_storage_gateway import MediaStorageGateway
from media_post_service_v2 import MediaPostServiceV2
from feed_composer import FeedComposer

class TestInstagramV2(unittest.TestCase):
    def setUp(self):
        self.follow_graph = FollowGraphService(celebrity_threshold=2)
        self.storage = MediaStorageGateway()
        self.post_service = MediaPostServiceV2(self.follow_graph, self.storage)
        self.composer = FeedComposer(self.post_service)

    def test_standard_fan_out_on_write(self):
        self.follow_graph.follow("u1", "u2")
        self.post_service.create_post("u2", b"img", "caption2")
        feed = self.composer.compose_feed("u1")
        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0].user_id, "u2")
        self.assertEqual(feed[0].caption, "caption2")

    def test_celebrity_fan_out_on_read(self):
        # make celeb a celebrity (threshold = 2)
        self.follow_graph.follow("u1", "celeb")
        self.follow_graph.follow("u2", "celeb")
        
        self.post_service.create_post("celeb", b"celeb_img", "celeb_cap")
        
        feed1 = self.composer.compose_feed("u1")
        self.assertEqual(len(feed1), 1)
        self.assertEqual(feed1[0].user_id, "celeb")
        
        # celeb's posts shouldn't be in u1's pre-computed push feed
        self.assertNotIn("celeb", [p.user_id for p in self.post_service.user_feeds.get("u1", [])])

    def test_pagination(self):
        self.follow_graph.follow("u1", "u2")
        self.post_service.create_post("u2", b"img1", "c1")
        
        self.post_service.create_post("u2", b"img2", "c2")
        
        self.post_service.create_post("u2", b"img3", "c3")
        
        feed_page1 = self.composer.compose_feed("u1", limit=2)
        self.assertEqual(len(feed_page1), 2)
        self.assertEqual(feed_page1[0].caption, "c3")
        self.assertEqual(feed_page1[1].caption, "c2")
        
        cursor = f"{feed_page1[-1].timestamp}_{feed_page1[-1].post_id}"
        feed_page2 = self.composer.compose_feed("u1", cursor=cursor, limit=2)
        self.assertEqual(len(feed_page2), 1)
        self.assertEqual(feed_page2[0].caption, "c1")

    def test_rollback_on_fanout_failure(self):
        class MockFollowGraph(FollowGraphService):
            def is_celebrity(self, user_id):
                return False # trigger fanout
            def get_followers(self, user_id):
                raise RuntimeError("Simulated fanout failure")
                
        mock_graph = MockFollowGraph(2)
        service = MediaPostServiceV2(mock_graph, self.storage)
        
        with self.assertRaises(RuntimeError) as context:
            service.create_post("u1", b"img", "cap")
            
        self.assertEqual(str(context.exception), "Simulated fanout failure")
        self.assertEqual(len(service.posts), 0, "Post should be rolled back")
        
    def test_unfollow_removes_posts(self):
        self.follow_graph.follow("u1", "u2")
        self.post_service.create_post("u2", b"img", "caption2")
        feed = self.composer.compose_feed("u1")
        self.assertEqual(len(feed), 1)
        
        self.follow_graph.unfollow("u1", "u2")
        feed2 = self.composer.compose_feed("u1")
        self.assertEqual(len(feed2), 0)

    def test_delete_post(self):
        self.follow_graph.follow("u1", "u2")
        post_id = self.post_service.create_post("u2", b"img", "caption2")
        feed = self.composer.compose_feed("u1")
        self.assertEqual(len(feed), 1)
        
        self.post_service.delete_post(post_id)
        feed2 = self.composer.compose_feed("u1")
        self.assertEqual(len(feed2), 0)

    def test_privacy(self):
        # u3 is public, u1 follows u3
        self.follow_graph.follow("u1", "u3")
        self.post_service.create_post("u3", b"img", "pub")
        self.assertEqual(len(self.composer.compose_feed("u1")), 1)
        
        # u3 goes private
        self.follow_graph.set_privacy("u3", True)
        # u1 is still a follower, should see it
        self.assertEqual(len(self.composer.compose_feed("u1")), 1)
        
        # u4 doesn't follow u3, shouldn't see it (if somehow they tried to fetch it, though compose_feed is only for home feed)
        # To test the privacy filter effectively, let's create a scenario where u4 unfollows u3
        self.follow_graph.follow("u4", "u3")
        post_id_2 = self.post_service.create_post("u3", b"img", "pub2")
        self.assertEqual(len(self.composer.compose_feed("u4")), 2)
        
        self.follow_graph.unfollow("u4", "u3")
        # Now u4 is not a follower. Even though u3's post might be in user_feeds or whatever (standard feed filtering handles unfollow),
        # the privacy filter ensures it's blocked.
        self.assertEqual(len(self.composer.compose_feed("u4")), 0)
        
        # Test celebrity privacy
        self.follow_graph.follow("u1", "celeb2")
        self.follow_graph.follow("u2", "celeb2") # celebrity threshold = 2
        self.post_service.create_post("celeb2", b"img", "c_post")
        self.assertEqual(len(self.composer.compose_feed("u1")), 2) # pub, c_post
        
        self.follow_graph.set_privacy("celeb2", True)
        self.assertEqual(len(self.composer.compose_feed("u1")), 2)
        
        self.follow_graph.unfollow("u1", "celeb2")
        self.assertEqual(len(self.composer.compose_feed("u1")), 1) # back to just pub

if __name__ == "__main__":
    unittest.main()
