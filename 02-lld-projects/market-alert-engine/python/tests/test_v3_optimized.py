import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))
for module_name in ["models", "engine"]:
    sys.modules.pop(module_name, None)

from models import Tick, AlertRule, PriceCondition, Operator, Sink
from engine import AlertEngine

class MockSink(Sink):
    def __init__(self):
        self.alert_count = 0
        self.lock = threading.Lock()
        self.events = []

    def send(self, rule: AlertRule, tick: Tick):
        with self.lock:
            self.alert_count += 1
            self.events.append((rule.rule_id, tick))
            
class SlowMockSink(Sink):
    def __init__(self, delay=0.1):
        self.alert_count = 0
        self.lock = threading.Lock()
        self.delay = delay

    def send(self, rule: AlertRule, tick: Tick):
        time.sleep(self.delay)
        with self.lock:
            self.alert_count += 1

def test_v3_concurrent_ingestion():
    engine = AlertEngine()
    sink = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    rule = AlertRule("rule1", "AAPL", condition, 0, [sink])
    engine.add_rule(rule)
    
    num_ticks = 1000
    for i in range(num_ticks):
        engine.process_tick(Tick("AAPL", 110.0, 100, 1000 + i))
        
    # Wait for queue to process
    engine.tick_queue.join()
    # Wait for dispatcher thread pool to finish
    engine.stop()
    
    assert sink.alert_count == num_ticks

def test_v3_cooldown_suppression():
    engine = AlertEngine()
    sink = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    rule = AlertRule("rule2", "MSFT", condition, 5000, [sink])
    engine.add_rule(rule)
    
    engine.process_tick(Tick("MSFT", 110.0, 100, 1000))
    engine.process_tick(Tick("MSFT", 110.0, 100, 2000))
    engine.process_tick(Tick("MSFT", 110.0, 100, 5999))
    engine.process_tick(Tick("MSFT", 110.0, 100, 6000))
    
    engine.tick_queue.join()
    engine.stop()
    
    assert sink.alert_count == 2

def test_v3_multisink_dispatch_async():
    engine = AlertEngine(num_workers=4)
    sink1 = SlowMockSink(0.1)
    sink2 = SlowMockSink(0.1)
    sink3 = SlowMockSink(0.1)
    
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    rule = AlertRule("rule3", "NVDA", condition, 0, [sink1, sink2, sink3])
    engine.add_rule(rule)
    
    start_time = time.time()
    # Ingestion should not be blocked
    engine.process_tick(Tick("NVDA", 150.0, 100, 1000))
    ingest_time = time.time() - start_time
    assert ingest_time < 0.05  # Ingest is fast
    
    engine.tick_queue.join()
    engine.stop()
    
    assert sink1.alert_count == 1
    assert sink2.alert_count == 1
    assert sink3.alert_count == 1

def test_v3_high_tick_volume():
    engine = AlertEngine(max_queue_size=20000)
    sink = MockSink()
    condition = PriceCondition(100.0, Operator.GREATER_THAN)
    # 5 seconds cooldown
    rule = AlertRule("rule4", "AMZN", condition, 5000, [sink])
    engine.add_rule(rule)
    
    num_threads = 50
    ticks_per_thread = 200
    
    def worker(thread_idx):
        for i in range(ticks_per_thread):
            # Same timestamp (1000) for all, so only 1 should get through cooldown
            engine.process_tick(Tick("AMZN", 150.0, 100, 1000))
            
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, i) for i in range(num_threads)]
        for f in as_completed(futures):
            f.result()
            
    engine.tick_queue.join()
    engine.stop()
    
    assert sink.alert_count == 1
