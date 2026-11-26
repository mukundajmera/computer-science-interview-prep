"""
News Feed Service - V2 Scaled

Fan-out on write with Redis caching.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
import threading
import queue
from feed_service import Post, PostRepository, FollowRepository, FeedService


class FeedCache(ABC):
    """Feed cache interface (Redis abstraction)."""
    
    @abstractmethod
    def add_to_feed(self, user_id: str, post_id: str, score: float) -> None:
        pass
    
    @abstractmethod
    def get_feed(self, user_id: str, max_score: float, limit: int) -> List[str]:
        pass
    
    @abstractmethod
    def trim_feed(self, user_id: str, max_size: int) -> None:
        pass


@dataclass
class FanoutMessage:
    """Message for fanout processing."""
    post_id: str
    author_id: str


class CachedFeedService(FeedService):
    """Cached feed service with fan-out on write."""
    
    CELEBRITY_THRESHOLD = 10000
    MAX_FEED_SIZE = 1000
    
    def __init__(self, post_repository: PostRepository,
                 follow_repository: FollowRepository,
                 feed_cache: FeedCache,
                 fanout_workers: int = 4):
        self._post_repository = post_repository
        self._follow_repository = follow_repository
        self._feed_cache = feed_cache
        self._fanout_queue: queue.Queue = queue.Queue()
        self._running = True
        self._workers: List[threading.Thread] = []
        
        # Start fanout workers
        for _ in range(fanout_workers):
            worker = threading.Thread(target=self._fanout_worker, daemon=True)
            worker.start()
            self._workers.append(worker)
    
    def create_post(self, user_id: str, content: str) -> Post:
        post = Post.create(user_id, content)
        self._post_repository.save(post)
        
        # Check if celebrity
        follower_count = self._follow_repository.get_follower_count(user_id)
        
        if follower_count < self.CELEBRITY_THRESHOLD:
            self._fanout_queue.put(FanoutMessage(post.post_id, user_id))
        
        return post
    
    def get_feed(self, user_id: str, cursor: Optional[str],
                limit: int) -> List[Post]:
        max_score = float(cursor) if cursor else datetime.utcnow().timestamp() * 1000
        
        # Get pre-computed feed from cache
        post_ids = self._feed_cache.get_feed(user_id, max_score, limit)
        
        # Get followed celebrities
        followees = self._follow_repository.get_followees(user_id)
        celebrities = [
            f for f in followees
            if self._follow_repository.get_follower_count(f) >= self.CELEBRITY_THRESHOLD
        ]
        
        # Fetch celebrity posts
        if celebrities:
            before = datetime.fromtimestamp(max_score / 1000)
            celeb_posts = self._post_repository.find_by_user_ids(
                celebrities, before, limit)
            for p in celeb_posts:
                if p.post_id not in post_ids:
                    post_ids.append(p.post_id)
        
        # Hydrate posts
        posts = []
        for post_id in post_ids:
            post = self._post_repository.find_by_id(post_id)
            if post:
                posts.append(post)
        
        # Sort and limit
        posts.sort(key=lambda p: p.created_at, reverse=True)
        return posts[:limit]
    
    def follow(self, follower_id: str, followee_id: str) -> None:
        self._follow_repository.add_follow(follower_id, followee_id)
        
        # Backfill recent posts
        recent_posts = self._post_repository.find_by_user_id(followee_id, 20)
        for post in recent_posts:
            self._feed_cache.add_to_feed(
                follower_id, post.post_id,
                post.created_at.timestamp() * 1000)
        self._feed_cache.trim_feed(follower_id, self.MAX_FEED_SIZE)
    
    def unfollow(self, follower_id: str, followee_id: str) -> None:
        self._follow_repository.remove_follow(follower_id, followee_id)
    
    def _fanout_worker(self):
        while self._running:
            try:
                message = self._fanout_queue.get(timeout=1.0)
                self._process_fanout(message)
            except queue.Empty:
                continue
    
    def _process_fanout(self, message: FanoutMessage):
        followers = self._follow_repository.get_followers(message.author_id)
        score = datetime.utcnow().timestamp() * 1000
        
        for follower_id in followers:
            self._feed_cache.add_to_feed(follower_id, message.post_id, score)
            self._feed_cache.trim_feed(follower_id, self.MAX_FEED_SIZE)
    
    def shutdown(self):
        self._running = False
        for worker in self._workers:
            worker.join(timeout=2.0)


class InMemoryFeedCache(FeedCache):
    """In-memory feed cache (simulating Redis)."""
    
    def __init__(self):
        self._feeds: Dict[str, Dict[float, str]] = {}
        self._lock = threading.Lock()
    
    def add_to_feed(self, user_id: str, post_id: str, score: float) -> None:
        with self._lock:
            if user_id not in self._feeds:
                self._feeds[user_id] = {}
            self._feeds[user_id][score] = post_id
    
    def get_feed(self, user_id: str, max_score: float, limit: int) -> List[str]:
        with self._lock:
            feed = self._feeds.get(user_id, {})
            result = []
            for score in sorted(feed.keys(), reverse=True):
                if score < max_score:
                    result.append(feed[score])
                    if len(result) >= limit:
                        break
            return result
    
    def trim_feed(self, user_id: str, max_size: int) -> None:
        with self._lock:
            feed = self._feeds.get(user_id, {})
            if len(feed) > max_size:
                sorted_scores = sorted(feed.keys(), reverse=True)
                for score in sorted_scores[max_size:]:
                    del feed[score]
