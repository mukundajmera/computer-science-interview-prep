from typing import List, Optional
try:
    from .media_post_service_v2 import MediaPostServiceV2, PostMetadata
except ImportError:
    from media_post_service_v2 import MediaPostServiceV2, PostMetadata

class FeedComposer:
    def __init__(self, post_service: MediaPostServiceV2):
        self.post_service = post_service
        self.follow_graph = post_service.follow_graph

    def compose_feed(self, user_id: str, cursor: Optional[str] = None, limit: int = 20) -> List[PostMetadata]:
        # Get standard feed (from fan-out-on-write)
        standard_feed = self.post_service.user_feeds.get(user_id, [])
        valid_followees = self.follow_graph.get_followees(user_id)
        
        # Filter standard feed to ensure we still follow the author (or self)
        filtered_standard = [
            p for p in standard_feed
            if (p.user_id == user_id or p.user_id in valid_followees) and p.post_id in self.post_service.posts
        ]
        
        # Pull celebrity posts (fan-out-on-read)
        celebrity_followees = {uid for uid in valid_followees if self.follow_graph.is_celebrity(uid)}
        
        celebrity_posts = []
        for post in self.post_service.posts.values():
            if post.user_id in celebrity_followees:
                celebrity_posts.append(post)
                
        # Merge feeds, deduplicating by post_id
        all_posts_map = {p.post_id: p for p in filtered_standard}
        for p in celebrity_posts:
            all_posts_map[p.post_id] = p
            
        all_posts = [p for p in all_posts_map.values() if not self.follow_graph.is_private(p.user_id) or p.user_id in valid_followees or p.user_id == user_id]
        
        # Sort by descending timestamp, then descending post_id (for stability)
        all_posts.sort(key=lambda p: (p.timestamp, p.post_id), reverse=True)

        # Filter by cursor (timestamp_postId)
        if cursor is not None:
            parts = cursor.split("_")
            cursor_timestamp = int(parts[0])
            cursor_post_id = parts[1]
            
            filtered = []
            for p in all_posts:
                if p.timestamp < cursor_timestamp or (p.timestamp == cursor_timestamp and p.post_id < cursor_post_id):
                    filtered.append(p)
            all_posts = filtered
        
        return all_posts[:limit]
