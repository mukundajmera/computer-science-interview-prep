from typing import List, Optional
from media_post_service_v3 import MediaPostServiceV3, PostMetadataV3
from follow_graph_service_v3 import FollowGraphServiceV3

class FeedComposerV3:
    def __init__(self, post_service: MediaPostServiceV3, follow_graph: FollowGraphServiceV3):
        self.post_service = post_service
        self.follow_graph = follow_graph

    def compose_feed(self, user_id: str, cursor: Optional[str] = None, limit: int = 10) -> List[PostMetadataV3]:
        standard_feed = self.post_service.get_user_feed(user_id)
        valid_followees = self.follow_graph.get_followees(user_id)
        
        filtered_standard = []
        for p in standard_feed:
            if (p.user_id == user_id or p.user_id in valid_followees) and self.post_service.get(p.post_id, p.region) is not None:
                filtered_standard.append(p)
                
        celebrity_followees = {uid for uid in valid_followees if self.follow_graph.is_celebrity(uid)}
        
        celebrity_posts = []
        for post in self.post_service.get_all_posts().values():
            if post.user_id in celebrity_followees:
                celebrity_posts.append(post)
                
        all_posts_dict = {p.post_id: p for p in filtered_standard}
        for p in celebrity_posts:
            all_posts_dict[p.post_id] = p
            
        all_posts = []
        for p in all_posts_dict.values():
            is_private = self.follow_graph.is_private(p.user_id)
            if not is_private or p.user_id == user_id or p.user_id in valid_followees:
                all_posts.append(p)
                
        all_posts.sort(key=lambda p: (p.timestamp, p.post_id), reverse=True)
        
        if cursor is not None:
            parts = cursor.split("_")
            cursor_timestamp = float(parts[0])
            cursor_post_id = parts[1]
            
            filtered = []
            for p in all_posts:
                if p.timestamp < cursor_timestamp or (p.timestamp == cursor_timestamp and p.post_id < cursor_post_id):
                    filtered.append(p)
            all_posts = filtered
            
        return all_posts[:limit]
