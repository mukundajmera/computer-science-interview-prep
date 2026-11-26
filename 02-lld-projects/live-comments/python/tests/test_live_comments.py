import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(__file__)
V1_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v1-basic"))
if V1_DIR not in sys.path:
    sys.path.insert(0, V1_DIR)

from comment_ingress_service import CommentIngressService


class CommentIngressServiceTest(unittest.TestCase):
    def setUp(self):
        # Small rate limit for testing: 2 comments per second
        self.service = CommentIngressService(buffer_size=10, rate_limit=2, window_sec=1.0)

    def test_publish_and_subscribe(self):
        self.service.subscribe("sub1", "video1")
        comment_id = self.service.publish_comment("video1", "user1", "Hello Live!")
        self.assertIsNotNone(comment_id)
        
        comments = self.service.get_comments("sub1")
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].content, "Hello Live!")

    def test_rate_limiting(self):
        # User 1 can publish 2 comments
        c1 = self.service.publish_comment("video2", "user1", "msg1")
        c2 = self.service.publish_comment("video2", "user1", "msg2")
        self.assertIsNotNone(c1)
        self.assertIsNotNone(c2)
        
        # 3rd comment should be rate limited
        c3 = self.service.publish_comment("video2", "user1", "msg3")
        self.assertIsNone(c3)

    def test_ring_buffer_overwrite(self):
        # Buffer size is 10
        for i in range(12):
            # Change user to avoid rate limit
            self.service.publish_comment("video3", f"user{i}", f"msg{i}")
            
        # Buffer should have overwritten the first 2 elements
        buffer_content = [c for c in self.service.ring_buffer if c is not None]
        self.assertEqual(len(buffer_content), 10)
        # Check latest comment
        latest_comment = self.service.ring_buffer[(self.service.write_index - 1) % 10]
        self.assertEqual(latest_comment.content, "msg11")

    def test_multiple_subscribers(self):
        self.service.subscribe("sub1", "video4")
        self.service.subscribe("sub2", "video4")
        
        self.service.publish_comment("video4", "user1", "Broadcast")
        
        c1 = self.service.get_comments("sub1")
        c2 = self.service.get_comments("sub2")
        
        self.assertEqual(len(c1), 1)
        self.assertEqual(len(c2), 1)
        self.assertEqual(c1[0].comment_id, c2[0].comment_id)


if __name__ == "__main__":
    unittest.main()
