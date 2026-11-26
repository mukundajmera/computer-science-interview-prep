import pytest
from datetime import datetime
import time
import sys
import os

# Add relevant directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-scaled'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-distributed'))

from feed_service import InMemoryPostRepository, InMemoryFollowRepository
from cached_feed_service import InMemoryFeedCache
from distributed_feed_service import DistributedFeedService, EngagementRanker

class TestDistributedFeedService:
    def setup_method(self):
        self.post_repo = InMemoryPostRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.feed_cache = InMemoryFeedCache()
        self.feed_ranker = EngagementRanker()
        self.service = DistributedFeedService(
            self.post_repo,
            self.follow_repo,
            self.feed_cache,
            self.feed_ranker
        )

    def teardown_method(self):
        if hasattr(self, 'service'):
            self.service.shutdown()

    def test_hybrid_fanout_for_regular_user(self):
        self.service.follow("userB", "userA")
        post = self.service.create_post("userA", "Post A")
        
        # Give some time for async fanout
        time.sleep(0.1)
        
        feed = self.service.get_feed("userB", None, 10)
        assert len(feed) == 1
        assert feed[0].post_id == post.post_id

    def test_hybrid_fanout_for_celebrity(self):
        # userA becomes a celebrity
        for i in range(10001):
            self.follow_repo.add_follow(f"user_{i}", "userA")
            
        post = self.service.create_post("userA", "Celeb Post")
        time.sleep(0.1)
        
        # user_0 follows userA, get feed fetches it dynamically
        feed = self.service.get_feed("user_0", None, 10)
        assert len(feed) == 1
        assert feed[0].post_id == post.post_id

    def test_feed_ranking(self):
        self.service.follow("userB", "userA")
        
        # Post 1: old, low engagement
        post1 = self.service.create_post("userA", "Post 1")
        time.sleep(0.01)
        
        # Post 2: new, treated normally
        post2 = self.service.create_post("userA", "Post 2")
        time.sleep(0.1)
        
        feed = self.service.get_feed("userB", None, 10)
        assert len(feed) == 2
        
        # Since recency is king and engagement is 0, newest should be first
        assert feed[0].post_id == post2.post_id
        assert feed[1].post_id == post1.post_id

