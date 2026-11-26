import pytest
from datetime import datetime
import time
import sys
import os

# Add v2-scaled directory to path, but v1-basic is also needed for the base classes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-scaled'))

from feed_service import InMemoryPostRepository, InMemoryFollowRepository
from cached_feed_service import CachedFeedService, InMemoryFeedCache

class TestCachedFeedService:
    def setup_method(self):
        self.post_repo = InMemoryPostRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.feed_cache = InMemoryFeedCache()
        self.service = CachedFeedService(
            self.post_repo, 
            self.follow_repo, 
            self.feed_cache,
            fanout_workers=2
        )

    def teardown_method(self):
        if hasattr(self, 'service'):
            self.service.shutdown()

    def test_fanout_for_regular_user(self):
        self.service.follow("userB", "userA")
        self.service.follow("userC", "userA")
        
        post = self.service.create_post("userA", "Hello Regular World!")
        
        # Wait for fanout processing
        time.sleep(0.1)
        
        feed_b = self.service.get_feed("userB", None, 10)
        assert len(feed_b) == 1
        assert feed_b[0].post_id == post.post_id
        
        feed_c = self.service.get_feed("userC", None, 10)
        assert len(feed_c) == 1

    def test_no_fanout_for_celebrity(self):
        # Make userA a celebrity
        for i in range(10001):
            self.follow_repo.add_follow(f"user_{i}", "userA")
            
        self.service.follow("userB", "userA")
        
        post = self.service.create_post("userA", "Hello Celebrity World!")
        
        # Wait for potential fanout processing
        time.sleep(0.1)
        
        # Ensure fanout does not put it in userB's cache
        cached_feed = self.feed_cache.get_feed("userB", datetime.utcnow().timestamp() * 1000 + 10000, 10)
        assert len(cached_feed) == 0
        
        # get_feed should fetch it dynamically
        feed = self.service.get_feed("userB", None, 10)
        assert len(feed) == 1
        assert feed[0].post_id == post.post_id

    def test_get_feed_combines_cached_and_celebrity(self):
        # userC is regular
        self.service.follow("userB", "userC")
        self.service.create_post("userC", "Regular post")
        
        # userA is celebrity
        for i in range(10001):
            self.follow_repo.add_follow(f"user_{i}", "userA")
        self.service.follow("userB", "userA")
        self.service.create_post("userA", "Celebrity post")
        
        time.sleep(0.1)
        
        feed = self.service.get_feed("userB", None, 10)
        assert len(feed) == 2
