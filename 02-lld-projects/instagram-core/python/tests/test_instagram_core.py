import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(__file__)
V1_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v1-basic"))
if V1_DIR not in sys.path:
    sys.path.insert(0, V1_DIR)

from media_post_service import MediaPostService


class MediaPostServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = MediaPostService()

    def test_create_and_get_post(self):
        post_id = self.service.create_post("user1", "http://example.com/img.jpg", "A nice pic")
        post = self.service.get_post(post_id)
        self.assertIsNotNone(post)
        self.assertEqual(post.user_id, "user1")
        self.assertEqual(post.media_url, "http://example.com/img.jpg")

    def test_follow_and_pull_feed(self):
        self.service.create_post("user2", "url1", "cap1")
        self.service.follow_user("user1", "user2")
        time.sleep(0.01)
        self.service.create_post("user2", "url2", "cap2")
        
        feed = self.service.get_feed("user1")
        self.assertEqual(len(feed), 2)
        self.assertEqual(feed[0].caption, "cap2")
        self.assertEqual(feed[1].caption, "cap1")

    def test_push_feed_active_user(self):
        # Make user1 active
        self.service.get_feed("user1")
        self.service.follow_user("user1", "user3")
        
        self.service.create_post("user3", "url3", "cap3")
        feed = self.service.get_feed("user1")
        self.assertTrue(any(p.caption == "cap3" for p in feed))

    def test_own_posts_in_feed(self):
        self.service.create_post("user4", "url4", "cap4")
        feed = self.service.get_feed("user4")
        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0].user_id, "user4")


if __name__ == "__main__":
    unittest.main()
