import sys
import os

# Add v1-basic to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from geohash_util import encode, decode, get_neighbors, haversine_distance
from proximity_service import ProximityService, Business

def test_geohash_encoding():
    lat, lon = 37.7749, -122.4194 # SF
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
    # Center
    service.add_business(Business("1", 37.7749, -122.4194))
    # Close by (approx 1km)
    service.add_business(Business("2", 37.7839, -122.4194))
    # Far away (approx 10km)
    service.add_business(Business("3", 37.8649, -122.4194))
    
    nearby_2km = service.get_nearby_businesses(37.7749, -122.4194, 2.0)
    assert len(nearby_2km) == 2
    assert "1" in [b.id for b in nearby_2km]
    assert "2" in [b.id for b in nearby_2km]
    
    nearby_20km = service.get_nearby_businesses(37.7749, -122.4194, 20.0)
    assert len(nearby_20km) == 3

def test_boundary_crossing():
    service = ProximityService()
    # Point near antimeridian
    service.add_business(Business("1", 0.0, 179.99))
    service.add_business(Business("2", 0.0, -179.99))
    
    # Distance should be small
    dist = haversine_distance(0.0, 179.99, 0.0, -179.99)
    assert dist < 5.0 # ~2.2km
    
    nearby = service.get_nearby_businesses(0.0, 180.0, 5.0)
    assert len(nearby) == 2

def test_haversine_distance_ranking():
    service = ProximityService()
    center_lat, center_lon = 40.7128, -74.0060 # NYC
    
    service.add_business(Business("b1", 40.7138, -74.0060)) # Closest
    service.add_business(Business("b2", 40.7158, -74.0060)) # Furthest
    service.add_business(Business("b3", 40.7148, -74.0060)) # Middle
    
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
