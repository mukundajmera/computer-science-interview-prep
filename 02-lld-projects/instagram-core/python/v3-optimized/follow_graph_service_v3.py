from typing import Set, Dict

class FollowGraphServiceV3:
    def __init__(self, celebrity_threshold: int):
        self.celebrity_threshold = celebrity_threshold
        self.followers: Dict[str, Set[str]] = {}
        self.followees: Dict[str, Set[str]] = {}
        self.privacy: Dict[str, bool] = {}

    def follow(self, follower_id: str, followee_id: str) -> None:
        self.followers.setdefault(followee_id, set()).add(follower_id)
        self.followees.setdefault(follower_id, set()).add(followee_id)

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        if followee_id in self.followers:
            self.followers[followee_id].discard(follower_id)
        if follower_id in self.followees:
            self.followees[follower_id].discard(followee_id)

    def get_followers(self, user_id: str) -> Set[str]:
        return self.followers.get(user_id, set())

    def get_followees(self, user_id: str) -> Set[str]:
        return self.followees.get(user_id, set())
        
    def is_celebrity(self, user_id: str) -> bool:
        return len(self.get_followers(user_id)) >= self.celebrity_threshold

    def set_privacy(self, user_id: str, is_private: bool) -> None:
        self.privacy[user_id] = is_private
        
    def is_private(self, user_id: str) -> bool:
        return self.privacy.get(user_id, False)
