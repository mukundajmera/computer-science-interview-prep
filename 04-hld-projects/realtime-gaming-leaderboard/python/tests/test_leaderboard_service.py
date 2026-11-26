import sys
import os
import pytest

# Insert v1-basic path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from leaderboard_service import LeaderboardService

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

    # ranks: 1: user10 (100) ... 10: user1 (10)
    # user8 is rank 3 (score 80)
    assert service.get_rank("user8") == 3
    
    # radius 2 from rank 3 -> ranks 1, 2, 3, 4, 5
    window = service.get_relative_window("user8", 2)
    assert len(window) == 5
    assert window[0].user_id == "user10"
    assert window[1].user_id == "user9"
    assert window[2].user_id == "user8"
    assert window[3].user_id == "user7"
    assert window[4].user_id == "user6"

    # radius 2 from rank 10 -> ranks 8, 9, 10
    window2 = service.get_relative_window("user1", 2)
    assert len(window2) == 3
    assert window2[0].user_id == "user3"
    assert window2[2].user_id == "user1"

def test_score_range_sharding():
    service = LeaderboardService(partition_size=100)
    service.increment_score("u1", 50, 1)    # part 0
    service.increment_score("u2", 150, 2)   # part 100
    service.increment_score("u3", 250, 3)   # part 200

    assert service.get_rank("u3") == 1
    assert service.get_rank("u2") == 2
    assert service.get_rank("u1") == 3

    # move u1 to part 300
    service.increment_score("u1", 300, 4)
    assert service.get_rank("u1") == 1
    assert service.get_rank("u3") == 2
    assert service.get_rank("u2") == 3
    assert service.get_score("u1") == 350

def test_tie_breaking_by_timestamp():
    service = LeaderboardService(partition_size=100)
    service.increment_score("u1", 100, 1005)  # middle
    service.increment_score("u2", 100, 1000)  # earliest
    service.increment_score("u3", 100, 1010)  # latest

    # Earlier timestamp ranks higher
    assert service.get_rank("u2") == 1
    assert service.get_rank("u1") == 2
    assert service.get_rank("u3") == 3

    top3 = service.get_top_k(3)
    assert top3[0].user_id == "u2"
    assert top3[1].user_id == "u1"
    assert top3[2].user_id == "u3"
