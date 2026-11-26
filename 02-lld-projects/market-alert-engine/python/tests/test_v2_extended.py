import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
for module_name in ["models", "engine"]:
    sys.modules.pop(module_name, None)

from models import Tick, AlertRule, PriceCondition, VolumeCondition, AndCondition, OrCondition, NotCondition, PercentChangeCondition, Operator, Sink
from engine import AlertEngine

class MockSink(Sink):
    def __init__(self):
        self.alert_count = 0
        self.lock = threading.Lock()

    def send(self, rule: AlertRule, tick: Tick):
        with self.lock:
            self.alert_count += 1

def test_v2_composite_dag():
    engine = AlertEngine()
    sink = MockSink()
    
    # DAG: (Price > 100 OR Vol > 500) AND NOT (Price == 150)
    c1 = PriceCondition(100.0, Operator.GREATER_THAN)
    c2 = VolumeCondition(500, Operator.GREATER_THAN)
    c3 = PriceCondition(150.0, Operator.EQUAL)
    
    or_cond = OrCondition(c1, c2)
    not_cond = NotCondition(c3)
    final_cond = AndCondition(or_cond, not_cond)
    
    rule = AlertRule("dag_rule", "AAPL", final_cond, 0, [sink])
    engine.add_rule(rule)
    
    # Match: Price > 100, not 150
    engine.process_tick(Tick("AAPL", 120.0, 100, 1000))
    assert sink.alert_count == 1
    
    # Match: Vol > 500, price not 150
    engine.process_tick(Tick("AAPL", 90.0, 600, 2000))
    assert sink.alert_count == 2
    
    # No match: Price == 150
    engine.process_tick(Tick("AAPL", 150.0, 600, 3000))
    assert sink.alert_count == 2

def test_v2_sliding_percentage():
    engine = AlertEngine()
    sink = MockSink()
    
    # 5% change in 10000ms
    condition = PercentChangeCondition(5.0, 10000)
    rule = AlertRule("pct_rule", "GOOG", condition, 0, [sink])
    engine.add_rule(rule)
    
    engine.process_tick(Tick("GOOG", 100.0, 100, 1000))
    assert sink.alert_count == 0
    
    engine.process_tick(Tick("GOOG", 102.0, 100, 2000)) # 2%
    assert sink.alert_count == 0
    
    engine.process_tick(Tick("GOOG", 106.0, 100, 3000)) # 6% change from 100
    assert sink.alert_count == 1
    
    # Let 100 drop out of the 10000ms window -> 13000ms
    engine.process_tick(Tick("GOOG", 107.0, 100, 13000))
    # Window has: (106 at 3000), (107 at 13000) -> max change is (107-106)/106 = ~0.94%
    assert sink.alert_count == 1
    
def test_v2_short_circuit_and():
    class SideEffectCondition(PriceCondition):
        def __init__(self):
            super().__init__(100.0, Operator.GREATER_THAN)
            self.evaluated = False
        def evaluate(self, tick: Tick) -> bool:
            self.evaluated = True
            return True
            
    engine = AlertEngine()
    sink = MockSink()
    
    c1 = PriceCondition(100.0, Operator.LESS_THAN) # Always false for 150
    c2 = SideEffectCondition()
    
    and_cond = AndCondition(c1, c2)
    rule = AlertRule("sc_and", "MSFT", and_cond, 0, [sink])
    engine.add_rule(rule)
    
    engine.process_tick(Tick("MSFT", 150.0, 100, 1000))
    assert sink.alert_count == 0
    assert c2.evaluated == False

def test_v2_short_circuit_or():
    class SideEffectCondition(PriceCondition):
        def __init__(self):
            super().__init__(100.0, Operator.GREATER_THAN)
            self.evaluated = False
        def evaluate(self, tick: Tick) -> bool:
            self.evaluated = True
            return True
            
    engine = AlertEngine()
    sink = MockSink()
    
    c1 = PriceCondition(50.0, Operator.LESS_THAN) # True for 40
    c2 = SideEffectCondition()
    
    or_cond = OrCondition(c1, c2)
    rule = AlertRule("sc_or", "AMZN", or_cond, 0, [sink])
    engine.add_rule(rule)
    
    engine.process_tick(Tick("AMZN", 40.0, 100, 1000))
    assert sink.alert_count == 1
    assert c2.evaluated == False
