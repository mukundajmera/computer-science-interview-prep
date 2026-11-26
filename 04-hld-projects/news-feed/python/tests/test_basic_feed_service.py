import pytest
from datetime import datetime
import time
import sys
import os

# Add the specific version directory to the path as instructed by memories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))

from feed_service import BasicFeedService, InMemoryPostRepository, InMemoryFollowRepository

class TestBasicFeedService:
    def setup_method(self):
        self.post_repo = InMemoryPostRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.service = BasicFeedService(self.post_repo, self.follow_repo)

    def test_create_post_and_get_feed(self):
        self.service.follow("userB", "userA")
        
        post1 = self.service.create_post("userA", "Post 1")
        time.sleep(0.01)  # ensure different timestamps
        post2 = self.service.create_post("userA", "Post 2")
        
        feed = self.service.get_feed("userB", None, 10)
        
        assert len(feed) == 2
        assert feed[0].post_id == post2.post_id
        assert feed[1].post_id == post1.post_id

    def test_empty_feed_if_no_followees(self):
        self.service.create_post("userA", "Post A")
        feed = self.service.get_feed("userB", None, 10)
        assert len(feed) == 0

    def test_unfollow_removes_posts_from_feed(self):
        self.service.follow("userB", "userA")
        self.service.create_post("userA", "Post A")
        
        feed_before = self.service.get_feed("userB", None, 10)
        assert len(feed_before) == 1
        
        self.service.unfollow("userB", "userA")
        
        feed_after = self.service.get_feed("userB", None, 10)
        assert len(feed_after) == 0

    def test_cannot_follow_yourself(self):
        with pytest.raises(ValueError):
            self.service.follow("userA", "userA")

    def test_cannot_create_empty_post(self):
        with pytest.raises(ValueError):
            self.service.create_post("userA", "")
