import time
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from follow_graph_service_v3 import FollowGraphServiceV3

@dataclass
class PostMetadataV3:
    post_id: str
    user_id: str
    media_key: str
    caption: str
    region: str
    timestamp: float = field(default_factory=time.time)

class IdempotencyStore:
    def __init__(self):
        # map key -> expiry timestamp
        self.store: Dict[str, float] = {}

    def claim(self, key: str, ttl_ms: int) -> bool:
        now = time.time()
        if key in self.store and self.store[key] > now:
            return False  # Already claimed and valid
        self.store[key] = now + (ttl_ms / 1000.0)
        return True

class DistributedRepository:
    def __init__(self):
        # key -> (value)
        self.store: Dict[str, PostMetadataV3] = {}

    def save(self, key: str, post: PostMetadataV3, region: str) -> None:
        self.store[key] = post

    def find(self, key: str, region: str) -> Optional[PostMetadataV3]:
        post = self.store.get(key)
        if post and post.region == region:
            return post
        return None
        
    def get_all_posts(self) -> Dict[str, PostMetadataV3]:
        return self.store.copy()
        
    def delete(self, key: str) -> None:
        self.store.pop(key, None)

class MediaPostServiceV3:
    def __init__(self, repository: DistributedRepository, idempotency: IdempotencyStore, follow_graph: FollowGraphServiceV3) -> None:
        self.repository = repository
        self.idempotency = idempotency
        self.follow_graph = follow_graph
        self.user_feeds: Dict[str, List[PostMetadataV3]] = {}
        self.clock = 1.0

    def upsert(self, post_id: str, user_id: str, media_key: str, caption: str, idempotency_key: str, region: str) -> bool:
        if not self.idempotency.claim(idempotency_key, 60_000):
            return False
        
        timestamp = self.clock
        self.clock += 1.0
        post = PostMetadataV3(post_id, user_id, media_key, caption, region, timestamp)
        self.repository.save(post_id, post, region)
        
        try:
            if not self.follow_graph.is_celebrity(user_id):
                for follower in self.follow_graph.get_followers(user_id):
                    self.user_feeds.setdefault(follower, []).append(post)
            self.user_feeds.setdefault(user_id, []).append(post)
        except Exception as e:
            # rollback
            self.repository.delete(post_id)
            for feed in self.user_feeds.values():
                if post in feed:
                    feed.remove(post)
            raise e

        return True

    def get(self, key: str, region: str) -> Optional[PostMetadataV3]:
        return self.repository.find(key, region)
        
    def get_all_posts(self) -> Dict[str, PostMetadataV3]:
        return self.repository.get_all_posts()
        
    def get_user_feed(self, user_id: str) -> List[PostMetadataV3]:
        return self.user_feeds.get(user_id, [])
        
    def delete_post(self, post_id: str) -> None:
        post = self.repository.get_all_posts().get(post_id)
        if post:
            self.repository.delete(post_id)
            for feed in self.user_feeds.values():
                try:
                    feed.remove(post)
                except ValueError:
                    pass
