import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MediaPost:
    post_id: str
    user_id: str
    media_url: str
    caption: str
    timestamp: float = field(default_factory=time.time)


class MediaPostService:
    def __init__(self):
        self.posts: Dict[str, MediaPost] = {}
        # Follow graph: user_id -> set of followed user_ids
        self.following: Dict[str, Set[str]] = defaultdict(set)
        # Push-based feed for active users: user_id -> list of post_ids
        self.user_feeds: Dict[str, List[str]] = defaultdict(list)
        # Simple simulation of active users
        self.active_users: Set[str] = set()

    def follow_user(self, follower_id: str, followee_id: str):
        self.following[follower_id].add(followee_id)
        # When a user follows someone, we might want to update their feed (Pull on read)
        # For simplicity, we just rely on the read operation to pull recent posts if needed.

    def create_post(self, user_id: str, media_url: str, caption: str) -> str:
        post_id = f"post_{len(self.posts) + 1}"
        post = MediaPost(post_id, user_id, media_url, caption)
        self.posts[post_id] = post

        # Fanout on write (Push)
        # In a real system, we'd find followers and push to their feeds.
        # Here we just iterate over all following lists to find followers.
        followers = [u for u, follows in self.following.items() if user_id in follows]
        for follower_id in followers:
            if follower_id in self.active_users:
                # Push to active users
                self.user_feeds[follower_id].insert(0, post_id)
                # Keep feed bounded
                if len(self.user_feeds[follower_id]) > 100:
                    self.user_feeds[follower_id].pop()
        
        # Self-feed push
        self.user_feeds[user_id].insert(0, post_id)
            
        return post_id

    def get_feed(self, user_id: str) -> List[MediaPost]:
        self.active_users.add(user_id)
        feed_post_ids = self.user_feeds[user_id]
        
        # Pull on read for inactive users or to complement push
        # If feed is empty or we want to ensure latest, we can pull from followees
        if not feed_post_ids:
            followed_users = self.following[user_id]
            all_recent_posts = []
            for post in self.posts.values():
                if post.user_id in followed_users or post.user_id == user_id:
                    all_recent_posts.append(post)
            # Sort by timestamp descending
            all_recent_posts.sort(key=lambda p: p.timestamp, reverse=True)
            # Update cache
            self.user_feeds[user_id] = [p.post_id for p in all_recent_posts[:100]]
            feed_post_ids = self.user_feeds[user_id]

        return [self.posts[pid] for pid in feed_post_ids if pid in self.posts]

    def get_post(self, post_id: str) -> Optional[MediaPost]:
        return self.posts.get(post_id)

