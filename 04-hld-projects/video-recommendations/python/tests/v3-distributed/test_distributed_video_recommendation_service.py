import pytest
import time
import os
import sys
from typing import List

# Ensure relative imports work by modifying sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_video_recommendation_service import (
    DistributedVideoRecommendationService,
    CandidateGenerator,
    RankingShard,
    VideoCandidate,
    RankScore
)

class DummyGenerator(CandidateGenerator):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def get_candidates(self, user_id: str, context_video_id: str, limit: int) -> List[VideoCandidate]:
        return [
            VideoCandidate(f"{self.prefix}1", "src", 1.0),
            VideoCandidate(f"{self.prefix}2", "src", 2.0)
        ]

class DummyShard(RankingShard):
    def __init__(self, shard_id: str, slow: bool = False, fail: bool = False):
        self.id = shard_id
        self.slow = slow
        self.fail = fail

    def rank_candidates(self, user_id: str, candidates: List[VideoCandidate]) -> List[RankScore]:
        if self.fail:
            raise RuntimeError("Shard failed")
        if self.slow:
            time.sleep(0.2) # 200ms
        return [RankScore(c.video_id, c.base_score * 10) for c in candidates]

    def get_shard_id(self) -> str:
        return self.id

@pytest.fixture
def service():
    generators = [DummyGenerator("A"), DummyGenerator("B")]
    shards = [DummyShard("S1"), DummyShard("S2")]
    svc = DistributedVideoRecommendationService(generators, shards, rank_timeout_ms=500)
    yield svc
    svc.shutdown()

def test_basic_distributed_retrieval_and_ranking(service):
    recs = service.get_recommendations("user1", "ctx", 10)
    assert len(recs) == 4
    assert set(recs) == {"A1", "A2", "B1", "B2"}

    # highest score first (B2 or A2 will have base_score 2.0 -> rank score 20)
    assert recs[0].endswith("2")

def test_timeout_fallback_on_slow_shard():
    generators = [DummyGenerator("A")]
    # Set timeout to 50ms, but shard takes 200ms
    shards = [DummyShard("S1", slow=True)]
    svc = DistributedVideoRecommendationService(generators, shards, rank_timeout_ms=50)

    recs = svc.get_recommendations("user1", "ctx", 10)
    assert len(recs) == 2

    # Since it timed out, fallback uses base scores (1.0 and 2.0).
    # "A2" has 2.0 base score.
    assert recs[0] == "A2"
    svc.shutdown()

def test_circuit_breaker_on_failing_shard():
    generators = [DummyGenerator("A")]
    shards = [DummyShard("S1", fail=True)]
    svc = DistributedVideoRecommendationService(generators, shards, rank_timeout_ms=500)

    # Multiple requests to trip the circuit breaker
    for _ in range(5):
        recs = svc.get_recommendations("user1", "ctx", 10)
        assert len(recs) == 2

    # Even when tripped, we get the fallback candidates.
    recs = svc.get_recommendations("user1", "ctx", 10)
    assert recs[0] == "A2"
    svc.shutdown()

def test_real_time_feedback_adjustments(service):
    # Normally A2 > A1 (20 vs 10 rank score)
    # But because there are 2 generators A and B, we only test adjusting one.
    recs_before = service.get_recommendations("user1", "ctx", 10)
    # the ones ending in 2 have highest score
    assert recs_before[0].endswith("2")

    # Let's adjust A2 to be very negative
    service.record_feedback("user1", "A2", "SKIP", 0)
    service.record_feedback("user1", "A2", "SKIP", 0) # -4
    for _ in range(5):
        service.record_feedback("user1", "A2", "SKIP", 0) # -10 more, total -14

    # Adjust A1 to be very positive
    service.record_feedback("user1", "A1", "LIKE", 0) # +5

    recs_after = service.get_recommendations("user1", "ctx", 10)

    # A1 should now beat A2. A1 score: 10 + 5 = 15. A2 score: 20 - 14 = 6.
    # We also have B1(10) and B2(20). So top should be B2(20), A1(15), B1(10), A2(6)
    assert recs_after[0] == "B2"
    assert recs_after[1] == "A1"
    assert recs_after[2] == "B1"
    assert recs_after[3] == "A2"
