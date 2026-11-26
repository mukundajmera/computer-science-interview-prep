import sys
import os
import pytest

# Memory context mentions: Python tests in this repository require dynamic sys.path imports. 
# To avoid ImportErrors with hyphenated directories (e.g., v1-basic), insert all required 
# version directories into the path (e.g., sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from metrics_leaderboard_service import MetricsLeaderboardService, LeaderboardSnapshot, LeaderboardEntry

class InMemoryMetricsLeaderboardService:
    def __init__(self):
        self.entries = []
        
    def ingest_point(self, metric_name: str, actor_id: str, value: float, timestamp_ms: int) -> None:
        self.entries.append(LeaderboardEntry(actor_id=actor_id, score=value, updated_at_ms=timestamp_ms))
        self.entries.sort(key=lambda x: x.score, reverse=True)

    def get_snapshot(self, leaderboard_id: str, limit: int) -> LeaderboardSnapshot:
        limited_entries = self.entries[:limit]
        return LeaderboardSnapshot(leaderboard_id=leaderboard_id, entries=limited_entries, computed_at_ms=1000000)

def test_ingest_point_and_get_snapshot():
    service = InMemoryMetricsLeaderboardService()
    service.ingest_point("views", "actor1", 10.0, 1000)
    
    snapshot = service.get_snapshot("views-leaderboard", 10)
    assert snapshot.leaderboard_id == "views-leaderboard"
    assert len(snapshot.entries) == 1
    assert snapshot.entries[0].actor_id == "actor1"
    assert snapshot.entries[0].score == 10.0
    assert snapshot.entries[0].updated_at_ms == 1000

def test_snapshot_respects_limit():
    service = InMemoryMetricsLeaderboardService()
    service.ingest_point("views", "actor1", 10.0, 1000)
    service.ingest_point("views", "actor2", 20.0, 1001)
    service.ingest_point("views", "actor3", 5.0, 1002)
    
    snapshot = service.get_snapshot("views-leaderboard", 2)
    assert len(snapshot.entries) == 2
    assert snapshot.entries[0].actor_id == "actor2"
    assert snapshot.entries[1].actor_id == "actor1"

def test_empty_snapshot():
    service = InMemoryMetricsLeaderboardService()
    snapshot = service.get_snapshot("views-leaderboard", 10)
    assert snapshot.leaderboard_id == "views-leaderboard"
    assert len(snapshot.entries) == 0
