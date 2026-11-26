import pytest
import threading
import sys
import os

def load_v1_modules():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
    import models
    import engine
    # Cleanup sys.path to not pollute
    sys.path.pop(0)
    return models, engine

models_v1, engine_v1 = load_v1_modules()

Driver = models_v1.Driver
Rider = models_v1.Rider
Location = models_v1.Location
DriverState = models_v1.DriverState
TripState = models_v1.TripState
PricingEngine = engine_v1.PricingEngine
MatchingEngine = engine_v1.MatchingEngine

def test_driver_fsm_lifecycle():
    driver = Driver("d1", Location(0, 0))
    assert driver.state == DriverState.OFFLINE
    
    assert driver.transition_state(DriverState.IDLE) is True
    assert driver.state == DriverState.IDLE
    
    # Invalid transition
    assert driver.transition_state(DriverState.IN_TRIP) is False
    assert driver.state == DriverState.IDLE
    
    assert driver.transition_state(DriverState.ASSIGNED) is True
    assert driver.transition_state(DriverState.IN_TRIP) is True
    assert driver.transition_state(DriverState.IDLE) is True
    assert driver.transition_state(DriverState.OFFLINE) is True
    assert driver.state == DriverState.OFFLINE

def test_dynamic_surge_pricing():
    pricing = PricingEngine(base_fare=5.0, per_mile_rate=2.0)
    
    # Low demand
    pricing.update_supply_demand(10, 1)
    surge = pricing.calculate_surge_multiplier()
    assert surge == 1.0
    
    # High demand
    pricing.update_supply_demand(0, 20) # Total: 10 drivers, 21 requests. Ratio > 2
    surge = pricing.calculate_surge_multiplier()
    assert surge == 2.0
    
    # Medium demand
    pricing.update_supply_demand(10, 0) # Total: 20 drivers, 21 requests. Ratio > 1, < 2
    surge = pricing.calculate_surge_multiplier()
    assert surge == 1.5

def test_nearest_driver_spatial_ranking():
    pricing = PricingEngine()
    engine = MatchingEngine(pricing)
    
    d1 = Driver("d1", Location(10, 10))
    d2 = Driver("d2", Location(2, 2))
    d3 = Driver("d3", Location(5, 5))
    d4 = Driver("d4", Location(20, 20)) # Outside radius
    
    d1.transition_state(DriverState.IDLE)
    d2.transition_state(DriverState.IDLE)
    d3.transition_state(DriverState.IDLE)
    d4.transition_state(DriverState.IDLE)
    
    engine.register_driver(d1)
    engine.register_driver(d2)
    engine.register_driver(d3)
    engine.register_driver(d4)
    
    # Rider at 0,0, default radius is 10.0
    # distances: d2 (2.82), d3 (7.07), d1 (14.14) -> d1 and d4 should be filtered out
    nearest = engine.find_nearest_drivers(Location(0, 0))
    
    assert len(nearest) == 2
    assert nearest[0].driver_id == "d2"
    assert nearest[1].driver_id == "d3"

def test_atomic_single_driver_dispatch():
    pricing = PricingEngine()
    engine = MatchingEngine(pricing)
    
    # Only 1 driver available
    driver = Driver("d1", Location(0, 0))
    driver.transition_state(DriverState.IDLE)
    engine.register_driver(driver)
    
    rider1 = Rider("r1", Location(1, 1))
    rider2 = Rider("r2", Location(1, 1))
    
    results = []
    def request_ride(rider):
        trip = engine.request_ride(rider, Location(5, 5))
        results.append(trip)
    
    t1 = threading.Thread(target=request_ride, args=(rider1,))
    t2 = threading.Thread(target=request_ride, args=(rider2,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # One trip should succeed, one should fail (be None)
    successes = [r for r in results if r is not None and r.state == TripState.ACCEPTED]
    assert len(successes) == 1
    assert successes[0].driver.driver_id == "d1"
    assert driver.state == DriverState.ASSIGNED

def test_no_driver_available():
    pricing = PricingEngine()
    engine = MatchingEngine(pricing)
    
    rider = Rider("r1", Location(1, 1))
    trip = engine.request_ride(rider, Location(5, 5))
    
    assert trip is None

def test_edge_cases():
    pricing = PricingEngine()
    engine = MatchingEngine(pricing)
    
    # Invalid input
    assert engine.request_ride(None, Location(0, 0)) is None
    
    # Duplicate operation
    d1 = Driver("d1", Location(1, 1))
    d1.transition_state(DriverState.IDLE)
    engine.register_driver(d1)
    engine.register_driver(d1)
    
    # Capacity boundary & Failure rollback
    r1 = Rider("r1", Location(1, 1))
    engine.update_driver_state("d1", DriverState.OFFLINE)
    t1 = engine.request_ride(r1, Location(5, 5))
    assert t1 is None

def test_location_timestamp_update():
    driver = Driver("d1", Location(0, 0, 100))
    # Older timestamp should be ignored
    driver.update_location(Location(1, 1, 90))
    assert driver.location.lat == 0
    assert driver.location.lon == 0
    
    # Newer timestamp should update
    driver.update_location(Location(2, 2, 110))
    assert driver.location.lat == 2
    assert driver.location.lon == 2
