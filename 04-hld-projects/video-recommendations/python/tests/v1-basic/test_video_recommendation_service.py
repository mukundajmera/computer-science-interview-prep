import pytest
import sys
import os

# Ensure the parent directory is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from video_recommendation_service import VideoRecommendationService, Video

@pytest.fixture
def service():
    srv = VideoRecommendationService()
    srv.add_video(Video("v1", "action", 0.8, 1000))
    srv.add_video(Video("v2", "comedy", 0.9, 2000))
    srv.add_video(Video("v3", "action", 0.5, 3000))
    srv.add_video(Video("v4", "drama", 0.7, 4000))
    srv.add_video(Video("v5", "action", 0.2, 5000))
    return srv

def test_candidate_generation_and_category_matching(service):
    service.record_watch_event("user1", "v1", 1.0, 6000)

    recs = service.get_recommendations("user1", 2, 7000)
    assert len(recs) == 2

    rec_ids = [v.id for v in recs]
    assert "v5" in rec_ids or "v3" in rec_ids

def test_popularity_fallback(service):
    recs = service.get_recommendations("new_user", 2, 7000)
    assert len(recs) == 2
    assert recs is not None

def test_unseen_video_filtering(service):
    service.record_watch_event("user1", "v1", 1.0, 6000)
    service.record_watch_event("user1", "v3", 1.0, 6000)
    service.record_watch_event("user1", "v5", 1.0, 6000)

    recs = service.get_recommendations("user1", 5, 7000)

    rec_ids = [v.id for v in recs]
    assert "v1" not in rec_ids
    assert "v3" not in rec_ids
    assert "v5" not in rec_ids
    assert "v2" in rec_ids
    assert "v4" in rec_ids

def test_top_k_ranking(service):
    service.record_watch_event("user1", "v1", 1.0, 6000)
    recs = service.get_recommendations("user1", 1, 7000)
    assert len(recs) == 1
    assert recs[0].id == "v5"
