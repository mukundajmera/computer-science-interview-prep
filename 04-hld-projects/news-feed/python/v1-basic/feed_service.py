"""
News Feed Service - V1 Basic

Core feed service implementation with pull-based approach.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Set, Dict
from abc import ABC, abstractmethod
import uuid


@dataclass
class Post:
    """Post entity."""
    post_id: str
    user_id: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    like_count: int = 0
    share_count: int = 0
    
    @staticmethod
    def create(user_id: str, content: str) -> 'Post':
        return Post(
            post_id=str(uuid.uuid4()),
            user_id=user_id,
            content=content
        )


class PostRepository(ABC):
    """Post repository interface."""
    
    @abstractmethod
    def save(self, post: Post) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, post_id: str) -> Optional[Post]:
        pass
    
    @abstractmethod
    def find_by_user_ids(self, user_ids: List[str], 
                        before: datetime, limit: int) -> List[Post]:
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str, limit: int) -> List[Post]:
        pass


class FollowRepository(ABC):
    """Follow graph repository interface."""
    
    @abstractmethod
    def add_follow(self, follower_id: str, followee_id: str) -> None:
        pass
    
    @abstractmethod
    def remove_follow(self, follower_id: str, followee_id: str) -> None:
        pass
    
    @abstractmethod
    def get_followees(self, user_id: str) -> Set[str]:
        pass
    
    @abstractmethod
    def get_followers(self, user_id: str) -> Set[str]:
        pass
    
    @abstractmethod
    def get_follower_count(self, user_id: str) -> int:
        pass


class FeedService(ABC):
    """Feed service interface."""
    
    @abstractmethod
    def create_post(self, user_id: str, content: str) -> Post:
        pass
    
    @abstractmethod
    def get_feed(self, user_id: str, cursor: Optional[str], 
                limit: int) -> List[Post]:
        pass
    
    @abstractmethod
    def follow(self, follower_id: str, followee_id: str) -> None:
        pass
    
    @abstractmethod
    def unfollow(self, follower_id: str, followee_id: str) -> None:
        pass


class BasicFeedService(FeedService):
    """Basic feed service - pull-based implementation."""
    
    def __init__(self, post_repository: PostRepository,
                 follow_repository: FollowRepository):
        self._post_repository = post_repository
        self._follow_repository = follow_repository
    
    def create_post(self, user_id: str, content: str) -> Post:
        if not content or not content.strip():
            raise ValueError("Post content cannot be empty")
        
        post = Post.create(user_id, content)
        self._post_repository.save(post)
        return post
    
    def get_feed(self, user_id: str, cursor: Optional[str],
                limit: int) -> List[Post]:
        # Get all users this person follows
        followees = self._follow_repository.get_followees(user_id)
        
        if not followees:
            return []
        
        # Parse cursor (ISO timestamp)
        before = datetime.fromisoformat(cursor) if cursor else datetime.utcnow()
        
        # Fetch posts from all followees
        posts = self._post_repository.find_by_user_ids(
            list(followees), before, limit)
        
        # Sort by created time descending
        posts.sort(key=lambda p: p.created_at, reverse=True)
        
        return posts[:limit]
    
    def follow(self, follower_id: str, followee_id: str) -> None:
        if follower_id == followee_id:
            raise ValueError("Cannot follow yourself")
        self._follow_repository.add_follow(follower_id, followee_id)
    
    def unfollow(self, follower_id: str, followee_id: str) -> None:
        self._follow_repository.remove_follow(follower_id, followee_id)


class InMemoryPostRepository(PostRepository):
    """In-memory post repository."""
    
    def __init__(self):
        self._posts: Dict[str, Post] = {}
        self._user_posts: Dict[str, List[Post]] = {}
    
    def save(self, post: Post) -> None:
        self._posts[post.post_id] = post
        if post.user_id not in self._user_posts:
            self._user_posts[post.user_id] = []
        self._user_posts[post.user_id].append(post)
    
    def find_by_id(self, post_id: str) -> Optional[Post]:
        return self._posts.get(post_id)
    
    def find_by_user_ids(self, user_ids: List[str],
                        before: datetime, limit: int) -> List[Post]:
        result = []
        for user_id in user_ids:
            user_posts = self._user_posts.get(user_id, [])
            for post in user_posts:
                if post.created_at < before:
                    result.append(post)
        
        result.sort(key=lambda p: p.created_at, reverse=True)
        return result[:limit]
    
    def find_by_user_id(self, user_id: str, limit: int) -> List[Post]:
        posts = self._user_posts.get(user_id, [])
        sorted_posts = sorted(posts, key=lambda p: p.created_at, reverse=True)
        return sorted_posts[:limit]


class InMemoryFollowRepository(FollowRepository):
    """In-memory follow repository."""
    
    def __init__(self):
        self._following: Dict[str, Set[str]] = {}
        self._followers: Dict[str, Set[str]] = {}
    
    def add_follow(self, follower_id: str, followee_id: str) -> None:
        if follower_id not in self._following:
            self._following[follower_id] = set()
        self._following[follower_id].add(followee_id)
        
        if followee_id not in self._followers:
            self._followers[followee_id] = set()
        self._followers[followee_id].add(follower_id)
    
    def remove_follow(self, follower_id: str, followee_id: str) -> None:
        if follower_id in self._following:
            self._following[follower_id].discard(followee_id)
        if followee_id in self._followers:
            self._followers[followee_id].discard(follower_id)
    
    def get_followees(self, user_id: str) -> Set[str]:
        return set(self._following.get(user_id, set()))
    
    def get_followers(self, user_id: str) -> Set[str]:
        return set(self._followers.get(user_id, set()))
    
    def get_follower_count(self, user_id: str) -> int:
        return len(self._followers.get(user_id, set()))
