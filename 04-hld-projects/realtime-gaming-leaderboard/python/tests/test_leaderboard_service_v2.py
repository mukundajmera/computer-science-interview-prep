import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from leaderboard_service_v2 import LeaderboardService

# ---------------------------------------------------------------------------
# v1 parity tests: same scenarios as tests/test_leaderboard_service.py, run
# against v2.
# ---------------------------------------------------------------------------

def test_zincrby_score_update():
    service = LeaderboardService(partition_size=100)
    service.increment_score("user1", 50, 1000)
    service.increment_score("user2", 30, 1001)

    assert service.get_score("user1") == 50
    assert service.get_rank("user1") == 1
    assert service.get_rank("user2") == 2

    # increment again
    service.increment_score("user2", 30, 1002)
    assert service.get_score("user2") == 60
    assert service.get_rank("user2") == 1
    assert service.get_rank("user1") == 2

def test_top_10_players_order():
    service = LeaderboardService(partition_size=100)
    for i in range(1, 16):
        service.increment_score(f"user{i}", i * 10, 1000 + i)

    top10 = service.get_top_k(10)
    assert len(top10) == 10
    assert top10[0].user_id == "user15"
    assert top10[0].score == 150
    assert top10[1].user_id == "user14"
    assert top10[1].score == 140
    assert top10[-1].user_id == "user6"
    assert top10[-1].score == 60

def test_user_rank_and_surrounding_players():
    service = LeaderboardService(partition_size=100)
    for i in range(1, 11):
        service.increment_score(f"user{i}", i * 10, 1000 + i)

    assert service.get_rank("user8") == 3

    window = service.get_relative_window("user8", 2)
    assert len(window) == 5
    assert window[0].user_id == "user10"
    assert window[1].user_id == "user9"
    assert window[2].user_id == "user8"
    assert window[3].user_id == "user7"
    assert window[4].user_id == "user6"

    window2 = service.get_relative_window("user1", 2)
    assert len(window2) == 3
    assert window2[0].user_id == "user3"
    assert window2[2].user_id == "user1"

def test_score_range_sharding():
    service = LeaderboardService(partition_size=100)
    service.increment_score("u1", 50, 1)
    service.increment_score("u2", 150, 2)
    service.increment_score("u3", 250, 3)

    assert service.get_rank("u3") == 1
    assert service.get_rank("u2") == 2
    assert service.get_rank("u1") == 3

    service.increment_score("u1", 300, 4)
    assert service.get_rank("u1") == 1
    assert service.get_rank("u3") == 2
    assert service.get_rank("u2") == 3
    assert service.get_score("u1") == 350

def test_tie_breaking_by_timestamp():
    service = LeaderboardService(partition_size=100)
    service.increment_score("u1", 100, 1005)
    service.increment_score("u2", 100, 1000)
    service.increment_score("u3", 100, 1010)

    assert service.get_rank("u2") == 1
    assert service.get_rank("u1") == 2
    assert service.get_rank("u3") == 3

    top3 = service.get_top_k(3)
    assert top3[0].user_id == "u2"
    assert top3[1].user_id == "u1"
    assert top3[2].user_id == "u3"

# ---------------------------------------------------------------------------
# v2-only tests: one or more per improvement.
# ---------------------------------------------------------------------------

# Improvement #1: cheat-resistant score validation (FOLLOW-UPS.md #3).

def test_max_increment_rejects_cheat():
    service = LeaderboardService(partition_size=100, max_increment=1000)
    assert service.increment_score("user1", 500, 1000) is True

    # A bot injecting a huge raw score is rejected.
    assert service.increment_score("user1", 9_999_999, 1001) is False

    assert service.get_score("user1") == 500, "rejected increment never applies"
    assert service.suspicious_rejected == 1
    assert service.get_rank("user1") == 1

def test_rejected_update_never_logged():
    service = LeaderboardService(partition_size=100, max_increment=1000)
    service.increment_score("user1", 100, 1000)
    service.increment_score("user1", 50_000, 1001)

    assert len(service.event_log) == 1, "only accepted updates reach the durable log"
    assert service.event_log[0] == ("user1", 100, 1000)

def test_validation_disabled_by_default_parity():
    service = LeaderboardService(partition_size=100)
    assert service.increment_score("user1", 9_999_999, 1000) is True
    assert service.get_score("user1") == 9_999_999

# Improvement #2: durable event log with replay rebuild (FOLLOW-UPS.md #4).

def test_event_log_records_all_accepted_updates():
    service = LeaderboardService(partition_size=100)
    service.increment_score("u1", 50, 1000)
    service.increment_score("u2", 70, 1001)
    service.increment_score("u1", 30, 1002)

    assert service.event_log == [("u1", 50, 1000), ("u2", 70, 1001), ("u1", 30, 1002)]

def test_replay_rebuilds_identical_state():
    service = LeaderboardService(partition_size=100)
    for i in range(1, 11):
        service.increment_score(f"user{i}", i * 10, 1000 + i)

    # Fresh primary rebuilt from the durable log after a failover.
    rebuilt = LeaderboardService(partition_size=100)
    rebuilt.replay_log(service.event_log)

    assert [e.user_id for e in rebuilt.get_top_k(10)] == [e.user_id for e in service.get_top_k(10)]
    for i in range(1, 11):
        assert rebuilt.get_rank(f"user{i}") == service.get_rank(f"user{i}")
        assert rebuilt.get_score(f"user{i}") == service.get_score(f"user{i}")

def test_replay_into_corrupted_service_recovers():
    service = LeaderboardService(partition_size=100)
    service.increment_score("u1", 100, 1000)
    service.increment_score("u2", 200, 1001)
    log = list(service.event_log)

    # Simulate catastrophic in-memory loss.
    service.partitions = {}
    service.user_scores = {}
    assert service.get_rank("u1") == -1

    service.replay_log(log)
    assert service.get_rank("u2") == 1
    assert service.get_rank("u1") == 2
    assert service.get_score("u1") == 100

# Improvement #3: hot-shard hash subdivision (FOLLOW-UPS.md #5).

def test_subdivision_preserves_global_order():
    plain = LeaderboardService(partition_size=100)
    subdivided = LeaderboardService(partition_size=100, dense_subdivisions=4)

    for i in range(1, 21):
        plain.increment_score(f"u{i}", i * 5, 1000 + i)       # scores 5..100, dense bucket
        subdivided.increment_score(f"u{i}", i * 5, 1000 + i)
    plain.increment_score("u1", 500, 2000)                     # push one out of the bucket
    subdivided.increment_score("u1", 500, 2000)

    assert [e.user_id for e in subdivided.get_top_k(20)] == [e.user_id for e in plain.get_top_k(20)]
    for i in range(1, 21):
        assert subdivided.get_rank(f"u{i}") == plain.get_rank(f"u{i}")
    assert len(subdivided.partitions[0]) == 4, "dense bucket split into 4 sub-shards"
    assert len(subdivided.partitions[500]) == 1, "other buckets are not subdivided"

def test_subdivision_relative_window_matches_plain():
    plain = LeaderboardService(partition_size=100)
    subdivided = LeaderboardService(partition_size=100, dense_subdivisions=3)

    for i in range(1, 13):
        plain.increment_score(f"p{i}", i * 7, 1000 + i)
        subdivided.increment_score(f"p{i}", i * 7, 1000 + i)

    target = "p6"
    plain_window = [e.user_id for e in plain.get_relative_window(target, 2)]
    sub_window = [e.user_id for e in subdivided.get_relative_window(target, 2)]
    assert sub_window == plain_window
    assert target in sub_window
