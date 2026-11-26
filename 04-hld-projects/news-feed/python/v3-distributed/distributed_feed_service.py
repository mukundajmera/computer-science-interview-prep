"""
News Feed Service - V3 Distributed

Hybrid fan-out with ranking and multi-region support.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import math

# Imports from previous versions
from feed_service import Post, PostRepository, FollowRepository, FeedService
from cached_feed_service import FeedCache


@dataclass
class RankedPost:
    """Post with ranking score."""
    post: Post
    score: float


class FeedRanker(ABC):
    """Feed ranking service interface."""
    
    @abstractmethod
    def rank(self, user_id: str, posts: List[Post]) -> List[RankedPost]:
        pass


class EngagementRanker(FeedRanker):
    """Simple chronological + engagement ranker."""
    
    def rank(self, user_id: str, posts: List[Post]) -> List[RankedPost]:
        ranked = []
        
        for post in posts:
            score = self._calculate_score(post)
            ranked.append(RankedPost(post=post, score=score))
        
        ranked.sort(key=lambda r: r.score, reverse=True)
        return ranked
    
    def _calculate_score(self, post: Post) -> float:
        # Base score from recency (hours since post)
        now = datetime.utcnow()
        age_hours = (now - post.created_at).total_seconds() / 3600
        recency_score = max(0, 100 - age_hours)
        
        # Engagement boost
        engagement_score = math.log10(
            1 + post.like_count + post.share_count * 2)
        
        return recency_score + engagement_score * 10


class DistributedFeedService(FeedService):
    """Distributed feed service with hybrid fan-out and ranking."""
    
    CELEBRITY_THRESHOLD = 10000
    MAX_FEED_SIZE = 1000
    BATCH_SIZE = 100
    
    def __init__(self, post_repository: PostRepository,
                 follow_repository: FollowRepository,
                 feed_cache: FeedCache,
                 feed_ranker: FeedRanker):
        self._post_repository = post_repository
        self._follow_repository = follow_repository
        self._feed_cache = feed_cache
        self._feed_ranker = feed_ranker
        self._executor = ThreadPoolExecutor(max_workers=8)
    
    def create_post(self, user_id: str, content: str) -> Post:
        post = Post.create(user_id, content)
        self._post_repository.save(post)
        
        # Async hybrid fan-out
        self._executor.submit(self._hybrid_fanout, post, user_id)
        
        return post
    
    def _hybrid_fanout(self, post: Post, author_id: str):
        followers = self._follow_repository.get_followers(author_id)
        follower_count = len(followers)
        
        if follower_count < self.CELEBRITY_THRESHOLD:
            # Fan-out on write for regular users
            self._fanout_to_followers(post, followers)
        else:
            # For celebrities, only fan-out to top engaged followers
            super_fans = self._get_top_engaged_followers(author_id, 1000)
            self._fanout_to_followers(post, super_fans)
    
    def _fanout_to_followers(self, post: Post, followers: Set[str]):
        score = post.created_at.timestamp() * 1000
        
        follower_list = list(followers)
        for i in range(0, len(follower_list), self.BATCH_SIZE):
            batch = follower_list[i:i + self.BATCH_SIZE]
            for follower_id in batch:
                self._feed_cache.add_to_feed(follower_id, post.post_id, score)
    
    def _get_top_engaged_followers(self, user_id: str, limit: int) -> Set[str]:
        # In production: Use engagement data
        all_followers = self._follow_repository.get_followers(user_id)
        return set(list(all_followers)[:limit])
    
    def get_feed(self, user_id: str, cursor: Optional[str],
                limit: int) -> List[Post]:
        max_score = float(cursor) if cursor else datetime.utcnow().timestamp() * 1000
        
        # Get pre-computed feed
        cached_post_ids = self._feed_cache.get_feed(user_id, max_score, limit * 2)
        
        # Get celebrity posts
        followees = self._follow_repository.get_followees(user_id)
        celebrity_posts = self._fetch_celebrity_posts(followees, max_score, limit)
        
        # Hydrate cached posts
        cached_posts = []
        for post_id in cached_post_ids:
            post = self._post_repository.find_by_id(post_id)
            if post:
                cached_posts.append(post)
        
        # Merge all posts
        seen = set()
        all_posts = []
        
        for post in cached_posts:
            if post.post_id not in seen:
                seen.add(post.post_id)
                all_posts.append(post)
        
        for post in celebrity_posts:
            if post.post_id not in seen:
                seen.add(post.post_id)
                all_posts.append(post)
        
        # Rank posts
        ranked = self._feed_ranker.rank(user_id, all_posts)
        
        # Return top N
        return [r.post for r in ranked[:limit]]
    
    def _fetch_celebrity_posts(self, followees: Set[str],
                              max_score: float, limit: int) -> List[Post]:
        celebrities = [
            f for f in followees
            if self._follow_repository.get_follower_count(f) >= self.CELEBRITY_THRESHOLD
        ]
        
        if not celebrities:
            return []
        
        before = datetime.fromtimestamp(max_score / 1000)
        return self._post_repository.find_by_user_ids(celebrities, before, limit)
    
    def follow(self, follower_id: str, followee_id: str) -> None:
        self._follow_repository.add_follow(follower_id, followee_id)
        
        # Backfill async
        def backfill():
            recent_posts = self._post_repository.find_by_user_id(followee_id, 50)
            for post in recent_posts:
                self._feed_cache.add_to_feed(
                    follower_id, post.post_id,
                    post.created_at.timestamp() * 1000)
            self._feed_cache.trim_feed(follower_id, self.MAX_FEED_SIZE)
        
        self._executor.submit(backfill)
    
    def unfollow(self, follower_id: str, followee_id: str) -> None:
        self._follow_repository.remove_follow(follower_id, followee_id)
    
    def shutdown(self):
        self._executor.shutdown(wait=True)


# ============================================================================
# Pattern Integration Hooks (Real-time transport, contention, workflow durability)
# ============================================================================

class DeliveryMode(Enum):
    POLLING = "POLLING"
    LONG_POLLING = "LONG_POLLING"
    SSE = "SSE"
    WEBSOCKET = "WEBSOCKET"
    # WebRTC could be used for media-heavy peer delivery when applicable.


class ContentionPolicy(Enum):
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    SERIAL_QUEUE = "SERIAL_QUEUE"
    DISTRIBUTED_LOCK = "DISTRIBUTED_LOCK"


@dataclass
class ExecutionResult:
    success: bool
    checkpoint_id: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False


class WorkflowStep(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def execute(self) -> ExecutionResult:
        ...


class CompensationStep(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def compensate(self, checkpoint_id: Optional[str]) -> None:
        ...


class WorkflowOrchestrator(ABC):
    @abstractmethod
    def run_step(self, step: WorkflowStep, idempotency_key: str, store: "IdempotencyStore") -> ExecutionResult:
        ...

    @abstractmethod
    def register_compensation(self, checkpoint_id: str, compensation_step: CompensationStep) -> None:
        ...


class IdempotencyStore(ABC):
    @abstractmethod
    def has_processed(self, key: str) -> bool:
        ...

    @abstractmethod
    def mark_processed(self, key: str, result: ExecutionResult) -> None:
        ...

    @abstractmethod
    def get_result(self, key: str) -> Optional[ExecutionResult]:
        ...
