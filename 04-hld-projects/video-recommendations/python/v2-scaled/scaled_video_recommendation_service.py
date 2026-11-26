from typing import List, Dict, Set
from collections import defaultdict
import random

class Video:
    def __init__(self, id: str, category: str, popularity: float, publish_time: int, tags: List[str] = None):
        self.id = id
        self.category = category
        self.popularity = popularity
        self.publish_time = publish_time
        self.tags = tags or []

class WatchEvent:
    def __init__(self, user_id: str, video_id: str, completion_percentage: float, timestamp: int):
        self.user_id = user_id
        self.video_id = video_id
        self.completion_percentage = completion_percentage
        self.timestamp = timestamp

class UserProfile:
    def __init__(self, user_id: str, category_affinity: Dict[str, float], watched_video_ids: Set[str], last_updated: int):
        self.user_id = user_id
        self.category_affinity = category_affinity
        self.watched_video_ids = watched_video_ids
        self.last_updated = last_updated

class ScaledVideoRecommendationService:
    def __init__(self):
        self.video_catalog: Dict[str, Video] = {}
        self.user_watch_history: Dict[str, List[WatchEvent]] = defaultdict(list)

        # User profile feature cache
        self.user_profile_cache: Dict[str, UserProfile] = {}
        self.profile_cache_ttl_ms = 60000  # 60 seconds

    def add_video(self, video: Video):
        self.video_catalog[video.id] = video

    def record_watch_event(self, user_id: str, video_id: str, completion_percentage: float, timestamp: int):
        self.user_watch_history[user_id].append(
            WatchEvent(user_id, video_id, completion_percentage, timestamp)
        )
        # Invalidate cache
        if user_id in self.user_profile_cache:
            del self.user_profile_cache[user_id]

    def _get_user_profile(self, user_id: str, current_time: int) -> UserProfile:
        cached = self.user_profile_cache.get(user_id)
        if cached and (current_time - cached.last_updated) < self.profile_cache_ttl_ms:
            return cached

        history = self.user_watch_history.get(user_id, [])
        watched_video_ids = {event.video_id for event in history}

        category_affinity = defaultdict(float)
        for event in history:
            video = self.video_catalog.get(event.video_id)
            if video:
                category_affinity[video.category] += event.completion_percentage

        profile = UserProfile(user_id, dict(category_affinity), watched_video_ids, current_time)
        self.user_profile_cache[user_id] = profile
        return profile

    def get_recommendations(self, user_id: str, k: int, current_time: int) -> List[Video]:
        profile = self._get_user_profile(user_id, current_time)

        # 1. Candidate Generation: Multi-source retrieval (Category, Trending, Graph/Tags)
        candidates: Set[Video] = set()

        # Category retrieval (based on top categories in affinity)
        top_categories = [cat for cat, _ in sorted(profile.category_affinity.items(), key=lambda item: item[1], reverse=True)[:3]]

        # Trending retrieval
        trending_videos = sorted(self.video_catalog.values(), key=lambda v: v.popularity, reverse=True)[:50]
        candidates.update(trending_videos)

        for video in self.video_catalog.values():
            if video.category in top_categories:
                candidates.add(video)

        # 2. Cold-start epsilon-greedy exploration
        is_cold_start = len(profile.watched_video_ids) == 0
        epsilon = 0.8 if is_cold_start else 0.1

        if random.random() < epsilon:
            all_videos = list(self.video_catalog.values())
            random.shuffle(all_videos)
            candidates.update(all_videos[:min(20, len(all_videos))])

        # Filter out already watched videos
        valid_candidates = [v for v in candidates if v.id not in profile.watched_video_ids]

        # 3. Heavy Ranking: multi-factor scoring with watch-time completion prediction and diversity penalty
        video_scores: Dict[str, float] = {}
        for video in valid_candidates:
            base_score = 0.0

            # Feature 1: Category Affinity
            affinity = profile.category_affinity.get(video.category, 0.0)
            base_score += affinity * 15.0

            # Feature 2: Popularity
            base_score += video.popularity * 2.0

            # Feature 3: Recency
            age_in_seconds = max(0, (current_time - video.publish_time) // 1000)
            recency_boost = 100.0 / (1.0 + age_in_seconds / 3600.0)
            base_score += recency_boost

            video_scores[video.id] = base_score

        # Sort by initial heavy rank
        valid_candidates.sort(key=lambda v: video_scores[v.id], reverse=True)

        # Apply Diversity Penalty during final selection
        final_recommendations: List[Video] = []
        category_counts: Dict[str, int] = defaultdict(int)

        for video in valid_candidates:
            if len(final_recommendations) >= k:
                break

            count = category_counts[video.category]
            diversity_penalty = count * 5.0

            # Here we simulate reranking or skipping due to penalty.
            # Simpler approach to enforce diversity constraint is skipping if too many
            if count < max(2, k // 3):
                final_recommendations.append(video)
                category_counts[video.category] += 1

        # Backfill if not enough recommendations
        if len(final_recommendations) < k:
            for video in valid_candidates:
                if len(final_recommendations) >= k:
                    break
                if video not in final_recommendations:
                    final_recommendations.append(video)

        return final_recommendations
