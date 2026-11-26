from typing import Set, Dict
from collections import defaultdict

class FollowGraphService:
    def __init__(self, celebrity_threshold: int = 10):
        self.celebrity_threshold = celebrity_threshold
        self.followers: Dict[str, Set[str]] = defaultdict(set)
        self.followees: Dict[str, Set[str]] = defaultdict(set)
        self.privacy: Dict[str, bool] = {}

    def follow(self, follower_id: str, followee_id: str) -> None:
        self.followers[followee_id].add(follower_id)
        self.followees[follower_id].add(followee_id)

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        self.followers[followee_id].discard(follower_id)
        self.followees[follower_id].discard(followee_id)

    def get_followers(self, user_id: str) -> Set[str]:
        return self.followers[user_id]

    def get_followees(self, user_id: str) -> Set[str]:
        return self.followees[user_id]
        
    def is_celebrity(self, user_id: str) -> bool:
        return len(self.followers[user_id]) >= self.celebrity_threshold
        
    def set_privacy(self, user_id: str, is_private: bool) -> None:
        self.privacy[user_id] = is_private
        
    def is_private(self, user_id: str) -> bool:
        return self.privacy.get(user_id, False)
