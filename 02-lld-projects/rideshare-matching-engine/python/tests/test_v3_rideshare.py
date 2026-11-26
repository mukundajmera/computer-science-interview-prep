import pytest
import threading
import sys
import os
import importlib.util

def load_v3_modules():
    spec = importlib.util.spec_from_file_location("rideshare_matching_engine", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized', 'rideshare_matching_engine.py')))
    module = importlib.util.module_from_spec(spec)
    sys.modules['rideshare_matching_engine'] = module
    sys.modules['models'] = module
    sys.modules['engine'] = module
    spec.loader.exec_module(module)
    return module

v3 = load_v3_modules()

Driver = v3.Driver
Rider = v3.Rider
Location = v3.Location
DriverState = v3.DriverState
TripState = v3.TripState
PricingEngine = v3.PricingEngine
MatchingEngine = v3.MatchingEngine
SpatialIndex = v3.SpatialIndex

def test_v3_spatial_index_gh():
    loc1 = Location(15.0, 25.0)
    assert loc1.to_geohash() == "1,2"

def test_v3_geohash_indexing():
    pricing = PricingEngine()
    matching = MatchingEngine(pricing)
    
    d1 = Driver("d1", Location(15.0, 25.0))
    d2 = Driver("d2", Location(16.0, 26.0))
    d3 = Driver("d3", Location(55.0, 55.0))
    
    d1.transition_state(DriverState.IDLE)
    d2.transition_state(DriverState.IDLE)
    d3.transition_state(DriverState.IDLE)
    
    matching.register_driver(d1)
    matching.register_driver(d2)
    matching.register_driver(d3)
    
    gh = "1,2"
    assert "d1" in matching.spatial_index.get_drivers_in_geohash(gh)
    assert "d2" in matching.spatial_index.get_drivers_in_geohash(gh)
    assert "d3" not in matching.spatial_index.get_drivers_in_geohash(gh)
    
    matching.update_driver_state("d1", DriverState.OFFLINE)
    assert "d1" not in matching.spatial_index.get_drivers_in_geohash(gh)

def test_v3_fast_find_nearest():
    pricing = PricingEngine()
    matching = MatchingEngine(pricing)
    
    d1 = Driver("d1", Location(12.0, 12.0))
    d1.transition_state(DriverState.IDLE)
    matching.register_driver(d1)
    
    r1 = Rider("r1", Location(11.0, 11.0))
    nearest = matching.find_nearest_drivers(r1.location)
    assert len(nearest) == 1
    assert nearest[0].driver_id == "d1"

def test_v3_batch_auction():
    pricing = PricingEngine()
    matching = MatchingEngine(pricing)
    
    d1 = Driver("d1", Location(1, 1))
    d2 = Driver("d2", Location(5, 5))
    d1.transition_state(DriverState.IDLE)
    d2.transition_state(DriverState.IDLE)
    
    matching.register_driver(d1)
    matching.register_driver(d2)
    
    r1 = Rider("r1", Location(1, 2))
    r2 = Rider("r2", Location(6, 6))
    
    t1 = matching.request_ride_batch(r1, Location(10, 10))
    t2 = matching.request_ride_batch(r2, Location(10, 10))
    
    assert len(matching.batch_queue) == 2
    
    matching.run_batch_auction()
    
    assert t1.state == TripState.ACCEPTED
    assert t2.state == TripState.ACCEPTED
    assert len(matching.batch_queue) == 0

def test_v3_edge_cases():
    pricing = PricingEngine()
    matching = MatchingEngine(pricing)
    
    # Invalid input
    assert matching.request_ride(None, Location(0, 0)) is None
    
    # Duplicate addition
    d1 = Driver("d1", Location(1, 1))
    d1.transition_state(DriverState.IDLE)
    matching.register_driver(d1)
    matching.register_driver(d1) # Duplicate
    assert len(matching.drivers) == 1
    
    # Capacity boundary / Rollback
    # Rider requests ride but driver state transition fails (simulated race)
    r1 = Rider("r1", Location(1, 1))
    matching.update_driver_state("d1", DriverState.OFFLINE) # Driver offline
    
    # No drivers available
    t1 = matching.request_ride(r1, Location(5, 5))
    assert t1 is None

