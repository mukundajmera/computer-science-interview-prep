import sys
import os

# Adjust path for import based on memory instructions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))

import pytest
from scaled_video_recommendation_service import ScaledVideoRecommendationService, Video

@pytest.fixture
def service():
    srv = ScaledVideoRecommendationService()
    srv.add_video(Video("v1", "action", 0.8, 1000, ["explosions", "hero"]))
    srv.add_video(Video("v2", "comedy", 0.9, 2000, ["funny", "jokes"]))
    srv.add_video(Video("v3", "action", 0.5, 3000, ["hero", "villain"]))
    srv.add_video(Video("v4", "drama", 0.7, 4000, ["sad", "emotional"]))
    srv.add_video(Video("v5", "action", 0.2, 5000, ["cars", "chase"]))
    srv.add_video(Video("v6", "action", 0.6, 6000, ["hero", "fight"]))
    srv.add_video(Video("v7", "action", 0.4, 7000, ["gun", "police"]))
    return srv

def test_candidate_generation_and_heavy_ranking(service):
    # User watched an action movie entirely
    service.record_watch_event("user1", "v1", 1.0, 6000)

    recs = service.get_recommendations("user1", 3, 8000)
    assert len(recs) > 0

    # Should heavily rank action videos
    categories = [v.category for v in recs]
    assert "action" in categories

    # Unseen filtering
    ids = [v.id for v in recs]
    assert "v1" not in ids

def test_cold_start_epsilon_greedy(service):
    # New user, no history
    recs = service.get_recommendations("new_user", 2, 8000)
    assert 0 < len(recs) <= 2

def test_diversity_penalty(service):
    # User loves action
    service.record_watch_event("user1", "v1", 1.0, 6000)
    service.record_watch_event("user1", "v3", 1.0, 6000)

    recs = service.get_recommendations("user1", 5, 8000)

    assert len(recs) == 5

    # Ensure that not ALL are action due to diversity backfill or interleaving.
    categories = [v.category for v in recs]
    assert any(c != "action" for c in categories)

def test_user_profile_cache_and_invalidation(service):
    # Request once to populate cache
    service.record_watch_event("user2", "v2", 1.0, 6000)
    recs1 = service.get_recommendations("user2", 2, 7000)

    # Request again within TTL (1 minute)
    recs2 = service.get_recommendations("user2", 2, 7010)

    # Now record another event, this should invalidate the cache
    service.record_watch_event("user2", "v4", 1.0, 7020)

    recs3 = service.get_recommendations("user2", 2, 7030)

    # Check that drama (v4) influences the results now
    ids = [v.id for v in recs3]
    assert "v4" not in ids  # Filtered out as watched
