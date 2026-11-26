import unittest
import sys
import os
import time

# Add repo root to path to allow importing _testutil
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)
from _testutil import load_module

v1_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v1-basic/feed_service.py")), "feed_service")

class TestBasicFeedService(unittest.TestCase):
    def setUp(self):
        self.post_repo = v1_mod.InMemoryPostRepository()
        self.follow_repo = v1_mod.InMemoryFollowRepository()
        self.service = v1_mod.BasicFeedService(
            post_repository=self.post_repo,
            follow_repository=self.follow_repo
        )
        
    def test_create_post(self):
        post = self.service.create_post("u1", "Hello world!")
        self.assertIsNotNone(post.post_id)
        self.assertEqual(post.user_id, "u1")
        self.assertEqual(post.content, "Hello world!")
        
        saved = self.post_repo.find_by_id(post.post_id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved.content, "Hello world!")
        
    def test_create_post_empty_content(self):
        with self.assertRaises(ValueError):
            self.service.create_post("u1", "")
        with self.assertRaises(ValueError):
            self.service.create_post("u1", "   ")
            
    def test_follow_and_unfollow(self):
        self.service.follow("u1", "u2")
        
        followees = self.follow_repo.get_followees("u1")
        self.assertIn("u2", followees)
        
        followers = self.follow_repo.get_followers("u2")
        self.assertIn("u1", followers)
        
        self.service.unfollow("u1", "u2")
        
        followees = self.follow_repo.get_followees("u1")
        self.assertNotIn("u2", followees)
        
    def test_follow_self(self):
        with self.assertRaises(ValueError):
            self.service.follow("u1", "u1")
            
    def test_get_feed_pulls_from_followees(self):
        self.service.follow("u1", "u2")
        self.service.follow("u1", "u3")
        
        post1 = self.service.create_post("u2", "Post from u2")
        time.sleep(0.01)
        post2 = self.service.create_post("u3", "Post from u3")
        time.sleep(0.01)
        post3 = self.service.create_post("u4", "Post from u4 (not followed)")
        
        feed = self.service.get_feed("u1", None, limit=10)
        self.assertEqual(len(feed), 2)
        
        # Newest first
        self.assertEqual(feed[0].post_id, post2.post_id)
        self.assertEqual(feed[1].post_id, post1.post_id)
        
    def test_get_feed_pagination(self):
        self.service.follow("u1", "u2")
        
        posts = []
        for i in range(5):
            post = self.service.create_post("u2", f"Post {i}")
            posts.append(post)
            time.sleep(0.01)
            
        # Get first 3
        feed1 = self.service.get_feed("u1", None, limit=3)
        self.assertEqual(len(feed1), 3)
        self.assertEqual(feed1[0].post_id, posts[4].post_id)
        self.assertEqual(feed1[2].post_id, posts[2].post_id)
        
        # Get next 2 using cursor
        cursor = feed1[2].created_at.isoformat()
        feed2 = self.service.get_feed("u1", cursor, limit=3)
        self.assertEqual(len(feed2), 2)
        self.assertEqual(feed2[0].post_id, posts[1].post_id)
        self.assertEqual(feed2[1].post_id, posts[0].post_id)

if __name__ == '__main__':
    unittest.main()
