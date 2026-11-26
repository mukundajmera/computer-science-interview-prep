import pytest
import threading
import sys
import os
import importlib.util

def load_v2_modules():
    spec_models = importlib.util.spec_from_file_location("models_v2_ext", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended', 'models.py')))
    models = importlib.util.module_from_spec(spec_models)
    old_models = sys.modules.get('models')
    sys.modules['models'] = models
    spec_models.loader.exec_module(models)
    
    spec_engine = importlib.util.spec_from_file_location("engine_v2_ext", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended', 'rideshare_matching_engine.py')))
    engine = importlib.util.module_from_spec(spec_engine)
    spec_engine.loader.exec_module(engine)
    
    if old_models:
        sys.modules['models'] = old_models
    else:
        del sys.modules['models']
        
    return models, engine

models_v2, engine_v2 = load_v2_modules()

Driver = models_v2.Driver
Rider = models_v2.Rider
Location = models_v2.Location
DriverState = models_v2.DriverState
TripState = models_v2.TripState
PricingEngine = engine_v2.PricingEngine
RideshareMatchingEngine = engine_v2.RideshareMatchingEngine

def test_v2_batch_auction_matching():
    pricing = PricingEngine()
    matching_engine = RideshareMatchingEngine(pricing)
    
    d1 = Driver("d1", Location(1, 1))
    d2 = Driver("d2", Location(5, 5))
    d1.transition_state(DriverState.IDLE)
    d2.transition_state(DriverState.IDLE)
    
    matching_engine.register_driver(d1)
    matching_engine.register_driver(d2)
    
    r1 = Rider("r1", Location(1, 2))
    r2 = Rider("r2", Location(6, 6))
    
    t1 = matching_engine.request_ride(r1, Location(10, 10))
    t2 = matching_engine.request_ride(r2, Location(10, 10))
    
    assert t1.state == TripState.REQUESTED
    assert t2.state == TripState.REQUESTED
    assert len(matching_engine.batch_queue) == 2
    
    matching_engine.run_batch_auction()
    
    assert t1.state == TripState.ACCEPTED
    assert t2.state == TripState.ACCEPTED
    assert t1.driver.driver_id == "d1"
    assert t2.driver.driver_id == "d2"
    assert len(matching_engine.batch_queue) == 0

def test_v2_batch_auction_unmatched():
    pricing = PricingEngine()
    matching_engine = RideshareMatchingEngine(pricing)
    
    d1 = Driver("d1", Location(1, 1))
    d1.transition_state(DriverState.IDLE)
    matching_engine.register_driver(d1)
    
    r1 = Rider("r1", Location(1, 2))
    r2 = Rider("r2", Location(6, 6))
    
    t1 = matching_engine.request_ride(r1, Location(10, 10))
    t2 = matching_engine.request_ride(r2, Location(10, 10))
    
    matching_engine.run_batch_auction()
    
    # One gets matched, one doesn't
    assert len(matching_engine.batch_queue) == 1
    if t1.state == TripState.ACCEPTED:
        assert t2.state == TripState.REQUESTED
    else:
        assert t1.state == TripState.REQUESTED
