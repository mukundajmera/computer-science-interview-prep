import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the v1-basic directory to the path so we can import the module correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
for module_name in ["models", "engine"]:
    sys.modules.pop(module_name, None)

from models import Tick, AlertRule, PriceCondition, VolumeCondition, AndCondition, Operator, Sink
from engine import AlertEngine

class MockSink(Sink):
    def __init__(self):
        self.alert_count = 0
        self.lock = threading.Lock()

    def send(self, rule: AlertRule, tick: Tick):
        with self.lock:
            self.alert_count += 1

def test_price_threshold_crossing():
    engine = AlertEngine()
    sink = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    rule = AlertRule("rule1", "AAPL", condition, 0, [sink])
    engine.add_rule(rule)

    engine.process_tick(Tick("AAPL", 90.0, 100, 1000))
    assert sink.alert_count == 0

    engine.process_tick(Tick("AAPL", 110.0, 100, 2000))
    assert sink.alert_count == 1

def test_composite_and_or_condition():
    engine = AlertEngine()
    sink = MockSink()
    
    price_cond = PriceCondition(100.0, Operator.GREATER_THAN)
    vol_cond = VolumeCondition(500, Operator.GREATER_THAN)
    and_cond = AndCondition(price_cond, vol_cond)
    
    rule = AlertRule("rule2", "GOOGL", and_cond, 0, [sink])
    engine.add_rule(rule)

    # Price > 100, Vol < 500
    engine.process_tick(Tick("GOOGL", 150.0, 100, 1000))
    assert sink.alert_count == 0

    # Price > 100, Vol > 500
    engine.process_tick(Tick("GOOGL", 150.0, 600, 2000))
    assert sink.alert_count == 1

def test_alert_cooldown_suppression():
    engine = AlertEngine()
    sink = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    
    rule = AlertRule("rule3", "MSFT", condition, 5000, [sink])
    engine.add_rule(rule)

    # Initial breach
    engine.process_tick(Tick("MSFT", 110.0, 100, 1000))
    assert sink.alert_count == 1

    # Suppressed (within 5000ms cooldown)
    engine.process_tick(Tick("MSFT", 115.0, 100, 2000))
    assert sink.alert_count == 1

    # Alert (cooldown expired: 6000 - 1000 >= 5000)
    engine.process_tick(Tick("MSFT", 120.0, 100, 6000))
    assert sink.alert_count == 2

def test_thread_safe_streaming():
    engine = AlertEngine()
    sink = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    rule = AlertRule("rule4", "AMZN", condition, 10000, [sink])
    engine.add_rule(rule)

    num_threads = 100
    tick = Tick("AMZN", 150.0, 100, 1000)

    def process():
        engine.process_tick(tick)

    # Note: Using as_completed handles concurrent execution but thread start order is OS dependent.
    # We create all futures, wait for them to finish, and assert the single evaluation logic holds.
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process) for _ in range(num_threads)]
        for future in as_completed(futures):
            future.result()

    # The lock ensures only 1 thread triggers the alert, the rest are suppressed by cooldown
    assert sink.alert_count == 1

def test_multiple_sinks():
    engine = AlertEngine()
    sink1 = MockSink()
    sink2 = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    
    rule = AlertRule("rule5", "NVDA", condition, 5000, [sink1, sink2])
    engine.add_rule(rule)

    engine.process_tick(Tick("NVDA", 110.0, 100, 1000))
    assert sink1.alert_count == 1
    assert sink2.alert_count == 1

def test_percent_change_condition():
    engine = AlertEngine()
    sink = MockSink()
    # 10% change in 5000ms
    from models import PercentChangeCondition
    condition = PercentChangeCondition(10.0, 5000)
    
    rule = AlertRule("rule6", "TSLA", condition, 0, [sink])
    engine.add_rule(rule)

    engine.process_tick(Tick("TSLA", 100.0, 100, 1000))
    assert sink.alert_count == 0
    
    # 105 is 5% change -> no alert
    engine.process_tick(Tick("TSLA", 105.0, 100, 2000))
    assert sink.alert_count == 0

    # 115 is 15% change from 100 -> alert
    engine.process_tick(Tick("TSLA", 115.0, 100, 3000))
    assert sink.alert_count == 1
    
    # Let the 100 and 105 fall out of the 5000ms window
    # 3000 + 5000 = 8000. So at 8001, previous ones are gone.
    engine.process_tick(Tick("TSLA", 118.0, 100, 8001))
    # Window now has (115 at 3000) and (118 at 8001) -> difference is (118-115)/115 = ~2.6% -> no new alert
    assert sink.alert_count == 1

