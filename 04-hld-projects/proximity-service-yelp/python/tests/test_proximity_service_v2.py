import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from geohash_util_v2 import encode, decode, get_neighbors, haversine_distance
from proximity_service_v2 import ProximityService, Business

# ---------------------------------------------------------------------------
# v1 parity tests: same scenarios as tests/test_proximity_service.py, run
# against v2.
# ---------------------------------------------------------------------------

def test_geohash_encoding():
    lat, lon = 37.7749, -122.4194  # SF
    geohash = encode(lat, lon, 6)
    assert len(geohash) == 6
    d_lat, d_lon = decode(geohash)
    assert abs(d_lat - lat) < 0.01
    assert abs(d_lon - lon) < 0.01

def test_neighbor_calculation():
    geohash = encode(37.7749, -122.4194, 6)
    neighbors = get_neighbors(geohash)
    assert len(neighbors) == 8
    assert geohash not in neighbors
    for n in neighbors:
        assert len(n) == 6

def test_nearby_search_radius():
    service = ProximityService()
    service.add_business(Business("1", 37.7749, -122.4194))
    service.add_business(Business("2", 37.7839, -122.4194))
    service.add_business(Business("3", 37.8649, -122.4194))

    nearby_2km = service.get_nearby_businesses(37.7749, -122.4194, 2.0)
    assert len(nearby_2km) == 2
    assert "1" in [b.id for b in nearby_2km]
    assert "2" in [b.id for b in nearby_2km]

    nearby_20km = service.get_nearby_businesses(37.7749, -122.4194, 20.0)
    assert len(nearby_20km) == 3

def test_boundary_crossing():
    service = ProximityService()
    service.add_business(Business("1", 0.0, 179.99))
    service.add_business(Business("2", 0.0, -179.99))

    dist = haversine_distance(0.0, 179.99, 0.0, -179.99)
    assert dist < 5.0  # ~2.2km

    nearby = service.get_nearby_businesses(0.0, 180.0, 5.0)
    assert len(nearby) == 2

def test_haversine_distance_ranking():
    service = ProximityService()
    center_lat, center_lon = 40.7128, -74.0060  # NYC

    service.add_business(Business("b1", 40.7138, -74.0060))  # Closest
    service.add_business(Business("b2", 40.7158, -74.0060))  # Furthest
    service.add_business(Business("b3", 40.7148, -74.0060))  # Middle

    results = service.get_nearby_businesses(center_lat, center_lon, 5.0)
    assert len(results) == 3
    assert results[0].id == "b1"
    assert results[1].id == "b3"
    assert results[2].id == "b2"

def test_business_upsert_and_removal():
    service = ProximityService()
    service.add_business(Business("1", 37.0, -122.0))

    results = service.get_nearby_businesses(37.0, -122.0, 1.0)
    assert len(results) == 1

    # Update location
    service.add_business(Business("1", 38.0, -122.0))
    results = service.get_nearby_businesses(37.0, -122.0, 1.0)
    assert len(results) == 0
    results = service.get_nearby_businesses(38.0, -122.0, 1.0)
    assert len(results) == 1

    # Remove
    service.remove_business("1")
    results = service.get_nearby_businesses(38.0, -122.0, 1.0)
    assert len(results) == 0

# ---------------------------------------------------------------------------
# v2-only tests: one or more per improvement.
# ---------------------------------------------------------------------------

# Improvement #1: dense-area pagination (FOLLOW-UPS.md #3).

def _dense_service():
    service = ProximityService()
    # 6 businesses in a line heading north from the query point.
    for i in range(1, 7):
        service.add_business(Business("b%d" % i, 37.7749 + i * 0.001, -122.4194))
    return service

def test_pagination_pages_in_distance_order():
    service = _dense_service()

    page1 = service.search_nearby(37.7749, -122.4194, 2.0, page_size=2, page=1)
    assert page1["total"] == 6
    assert [b.id for b in page1["businesses"]] == ["b1", "b2"], "page 1 is the true closest"

    page2 = service.search_nearby(37.7749, -122.4194, 2.0, page_size=2, page=2)
    assert [b.id for b in page2["businesses"]] == ["b3", "b4"]

    page3 = service.search_nearby(37.7749, -122.4194, 2.0, page_size=2, page=3)
    assert [b.id for b in page3["businesses"]] == ["b5", "b6"]

def test_pagination_beyond_end_and_validation():
    service = _dense_service()

    beyond = service.search_nearby(37.7749, -122.4194, 2.0, page_size=2, page=4)
    assert beyond["businesses"] == []
    assert beyond["total"] == 6, "total counts all matches, not the page"

    with pytest.raises(ValueError):
        service.search_nearby(37.7749, -122.4194, 2.0, page_size=0)
    with pytest.raises(ValueError):
        service.search_nearby(37.7749, -122.4194, 2.0, page=0)

# Improvement #2: attribute filtering (FOLLOW-UPS.md #4).

def test_filter_by_category():
    service = ProximityService()
    service.add_business(Business("r1", 37.7759, -122.4194, category="restaurant"))
    service.add_business(Business("c1", 37.7769, -122.4194, category="cafe"))

    result = service.search_nearby(37.7749, -122.4194, 2.0, category="cafe")
    assert [b.id for b in result["businesses"]] == ["c1"]
    assert result["total"] == 1

def test_filter_by_min_rating_and_open_now():
    service = ProximityService()
    service.add_business(Business("low", 37.7759, -122.4194, rating=3.5))
    service.add_business(Business("high-closed", 37.7769, -122.4194, rating=4.8, open_now=False))
    service.add_business(Business("high-open", 37.7779, -122.4194, rating=4.5, open_now=True))

    result = service.search_nearby(37.7749, -122.4194, 2.0, min_rating=4.0, open_now=True)
    assert [b.id for b in result["businesses"]] == ["high-open"]

    all_rated = service.search_nearby(37.7749, -122.4194, 2.0, min_rating=4.0)
    assert [b.id for b in all_rated["businesses"]] == ["high-closed", "high-open"]

# Improvement #3: geohash-prefix sharding with observability
# (FOLLOW-UPS.md #1).

def test_sharded_query_touches_only_relevant_shards():
    service = ProximityService()
    # SF and NYC: different first-character geohash shards.
    service.add_business(Business("sf1", 37.7749, -122.4194))
    service.add_business(Business("nyc1", 40.7128, -74.0060))

    assert len(service.shards) == 2, "businesses land in different shards"

    service.get_nearby_businesses(37.7749, -122.4194, 2.0)
    assert service.last_query_shards_touched == 1, "SF query scans only the SF shard"
    assert service.queries_run == 1

def test_sharded_index_finds_same_results_as_full_scan():
    service = ProximityService()
    points = [
        ("a", 37.7749, -122.4194), ("b", 37.7849, -122.4094),
        ("c", 37.7649, -122.4294), ("d", 38.7749, -122.4194),
    ]
    for pid, lat, lon in points:
        service.add_business(Business(pid, lat, lon))

    found = service.get_nearby_businesses(37.7749, -122.4194, 3.0)
    found_ids = [b.id for b in found]

    # Independent full scan without the shard structure.
    expected = sorted(
        (haversine_distance(37.7749, -122.4194, lat, lon), pid)
        for pid, lat, lon in points
        if haversine_distance(37.7749, -122.4194, lat, lon) <= 3.0
    )
    assert found_ids == [pid for dist, pid in expected]

def test_removal_cleans_empty_shard():
    service = ProximityService()
    service.add_business(Business("only", 37.7749, -122.4194))
    assert len(service.shards) == 1

    service.remove_business("only")
    assert len(service.shards) == 0, "empty shards are reclaimed"
