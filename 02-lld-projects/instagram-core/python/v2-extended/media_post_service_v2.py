import time
import itertools
import uuid
from typing import List, Optional, Dict
from dataclasses import dataclass, field

try:
    from .follow_graph_service import FollowGraphService
    from .media_storage_gateway import MediaStorageGateway
except ImportError:
    from follow_graph_service import FollowGraphService
    from media_storage_gateway import MediaStorageGateway

@dataclass
class PostMetadata:
    post_id: str
    user_id: str
    media_key: str
    caption: str
    timestamp: int

class MediaPostServiceV2:
    def __init__(self, follow_graph: FollowGraphService, storage: MediaStorageGateway):
        self.follow_graph = follow_graph
        self.storage = storage
        self.posts: Dict[str, PostMetadata] = {}
        # standard user feeds (push-based / fan-out-on-write)
        self.user_feeds: Dict[str, List[PostMetadata]] = {}
        self._clock = itertools.count(1)
        
    def create_post(self, user_id: str, media_bytes: bytes, caption: str) -> str:
        media_key = self.storage.put(media_bytes)
        post_id = str(uuid.uuid4())
        post = PostMetadata(post_id, user_id, media_key, caption, next(self._clock))
        self.posts[post_id] = post
        
        try:
            # If user is not a celebrity, fan-out-on-write to all followers
            if not self.follow_graph.is_celebrity(user_id):
                followers = self.follow_graph.get_followers(user_id)
                for follower in followers:
                    if follower not in self.user_feeds:
                        self.user_feeds[follower] = []
                    self.user_feeds[follower].append(post)
                    
            # Also push to own feed
            if user_id not in self.user_feeds:
                self.user_feeds[user_id] = []
            self.user_feeds[user_id].append(post)
        except Exception as e:
            # rollback
            self.posts.pop(post_id, None)
            for feed in self.user_feeds.values():
                try:
                    feed.remove(post)
                except ValueError:
                    pass
            raise e

        return post_id
        
    def get_post(self, post_id: str) -> Optional[PostMetadata]:
        return self.posts.get(post_id)
        
    def delete_post(self, post_id: str) -> None:
        post = self.posts.pop(post_id, None)
        if post:
            # Remove from all user feeds
            for feed in self.user_feeds.values():
                try:
                    feed.remove(post)
                except ValueError:
                    pass
