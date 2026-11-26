from typing import List, Dict, Set
from collections import defaultdict

class Video:
    def __init__(self, id: str, category: str, popularity: float, publish_time: int):
        self.id = id
        self.category = category
        self.popularity = popularity
        self.publish_time = publish_time

class WatchEvent:
    def __init__(self, user_id: str, video_id: str, completion_percentage: float, timestamp: int):
        self.user_id = user_id
        self.video_id = video_id
        self.completion_percentage = completion_percentage
        self.timestamp = timestamp

class VideoRecommendationService:
    def __init__(self):
        self.video_catalog: Dict[str, Video] = {}
        self.user_watch_history: Dict[str, List[WatchEvent]] = defaultdict(list)

    def add_video(self, video: Video):
        self.video_catalog[video.id] = video

    def record_watch_event(self, user_id: str, video_id: str, completion_percentage: float, timestamp: int):
        self.user_watch_history[user_id].append(
            WatchEvent(user_id, video_id, completion_percentage, timestamp)
        )

    def get_recommendations(self, user_id: str, k: int, current_time: int) -> List[Video]:
        history = self.user_watch_history.get(user_id, [])
        watched_video_ids = {event.video_id for event in history}

        category_affinity = defaultdict(float)
        for event in history:
            video = self.video_catalog.get(event.video_id)
            if video:
                category_affinity[video.category] += event.completion_percentage

        candidates = []
        video_scores = {}

        for video in self.video_catalog.values():
            if video.id in watched_video_ids:
                continue

            score = 0.0

            affinity = category_affinity.get(video.category, 0.0)
            if affinity > 0:
                score += affinity * 20
            else:
                score += video.popularity

            age_in_seconds = max(0, (current_time - video.publish_time) // 1000)
            recency_boost = 100.0 / (1.0 + age_in_seconds / 3600.0)
            score += recency_boost

            video_scores[video.id] = score
            candidates.append(video)

        candidates.sort(key=lambda v: video_scores[v.id], reverse=True)

        return candidates[:k]
