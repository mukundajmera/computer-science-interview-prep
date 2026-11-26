import os
import sys
import time
import unittest
import threading

BASE_DIR = os.path.dirname(__file__)

# Fix import paths due to hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..", "v1-basic")))
import domain as v1_domain
import price_tracker as v1_tracker

sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..", "v2-extended")))
import dispatcher as v2_dispatcher
import price_service as v2_service
import price_collector as v2_collector

sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..", "v3-optimized")))
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "v3-optimized")))
import dispatcher as v3_dispatcher
import price_service as v3_service
import price_collector as v3_collector
import ring_buffer as v3_buffer
sys.path.pop(0)

# V1 Tests
class Testv1_store_and_query_current(unittest.TestCase):
        def runTest(self):
            store = v1_tracker.PriceHistoryStore()
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1000, 1500, True))
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1005, 1200, True))
            assert store.get_current_price("p1", "m1") == 1200

class Testv1_min_max_price(unittest.TestCase):
        def runTest(self):
            store = v1_tracker.PriceHistoryStore()
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1000, 1500, True))
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1005, 1200, True))
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1010, 1800, True))
            assert store.get_min_price("p1", "m1") == 1200
            assert store.get_max_price("p1", "m1") == 1800

class Testv1_percentage_change(unittest.TestCase):
        def runTest(self):
            store = v1_tracker.PriceHistoryStore()
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1000, 1000, True))
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1005, 1500, True))
            store.add_price_tick("p1", "m1", v1_domain.PriceRecord(1010, 800, True))
            
            change = store.get_percentage_change("p1", "m1", 1000, 1005)
            assert change == 50.0  # (1500 - 1000) / 1000
            
            change_drop = store.get_percentage_change("p1", "m1", 1000, 1010)
            assert change_drop == -20.0 # (800 - 1000) / 1000

class Testv1_empty_store(unittest.TestCase):
        def runTest(self):
            store = v1_tracker.PriceHistoryStore()
            assert store.get_current_price("p2", "m2") is None
            assert store.get_min_price("p2", "m2") is None
            assert store.get_percentage_change("p2", "m2", 0, 100) is None

# Mock dependencies for V2 tests
class MockAdapter(v2_dispatcher.ChannelAdapter):
            def __init__(self):
                self.sent_messages = []
            def send(self, user_id: str, message: str) -> None:
                self.sent_messages.append((user_id, message))

class MockClock:
            def __init__(self, time_sec: int):
                self.time_sec = time_sec
            def now_sec(self) -> int:
                return self.time_sec
            def advance(self, seconds: int):
                self.time_sec += seconds

class MockTransport(v2_collector.Transport):
            def fetch_price(self, product_id: str, merchant_id: str) -> int:
                if product_id == "missing":
                    return None
                return 1500

# V2 Tests
class Testv2_threshold_alert_and_unsubscribe(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v2_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v2_service.InMemoryPriceHistoryStore(retention_seconds=3600, clock=clock)
            service = v2_service.PriceService(store, dispatcher)
            
            sub = v1_domain.PriceAlertSubscription("sub1", "u1", "p1", threshold_price=1000, channel=v1_domain.Channel.EMAIL)
            service.subscribe(sub)
            
            # Initial price above threshold
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1200, True))
            assert len(adapter.sent_messages) == 0
            
            # Price drops below threshold - triggers alert
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 900, True))
            assert len(adapter.sent_messages) == 1
            
            # Price stays below threshold - no new alert (crossing logic)
            clock.advance(70) # past rate limit
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 800, True))
            assert len(adapter.sent_messages) == 1
            
            # Price goes above threshold
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1100, True))
            assert len(adapter.sent_messages) == 1
            
            # Price drops below threshold again - triggers alert
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 950, True))
            assert len(adapter.sent_messages) == 2
            
            # Unsubscribe
            service.unsubscribe("sub1")
            
            # Price drops - no alert
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 850, True))
            assert len(adapter.sent_messages) == 2

class Testv2_out_of_order_timestamps_and_retention(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v2_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v2_service.InMemoryPriceHistoryStore(retention_seconds=3600, clock=clock)
            service = v2_service.PriceService(store, dispatcher)
            
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1200, True))
            
            # Out of order timestamp (earlier)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec() - 100, 900, True))
            
            # Current price should still be 1200
            assert store.get_current_price("p1", "m1") == 1200
            
            # Fast forward 2 hours
            clock.advance(7200)
            
            # New update
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1100, True))
            
            # Old records should be cleaned up
            assert len(store.get_history("p1", "m1")) == 1
            assert store.get_current_price("p1", "m1") == 1100

class Testv2_price_collector(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v2_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v2_service.InMemoryPriceHistoryStore(retention_seconds=3600, clock=clock)
            service = v2_service.PriceService(store, dispatcher)
            
            transport = MockTransport()
            collector = v2_collector.PriceCollector(
                price_service=service,
                product_ids=["p1", "missing"],
                merchant_ids=["m1"],
                transport=transport,
                clock=clock
            )
            
            collector.poll()
            
            assert store.get_current_price("p1", "m1") == 1500
            assert store.get_current_price("missing", "m1") is None

class Testv2_percentage_drop_alert(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v2_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v2_service.InMemoryPriceHistoryStore(retention_seconds=48 * 3600, clock=clock) # Need at least 24h retention
            service = v2_service.PriceService(store, dispatcher)
            
            sub = v1_domain.PriceAlertSubscription("sub2", "u2", "p2", percentage_drop=20.0, channel=v1_domain.Channel.EMAIL)
            service.subscribe(sub)
            
            old_time = clock.now_sec() - (25 * 60 * 60) # 25 hours ago
            service.on_price_update("p2", "m2", v1_domain.PriceRecord(old_time, 1000, True))
            
            # 10% drop, should not trigger
            service.on_price_update("p2", "m2", v1_domain.PriceRecord(clock.now_sec(), 900, True))
            assert len(adapter.sent_messages) == 0
            
            # Wait to reset rate limit for a real test, but we can bypass rate limit logic by sending a different subscription id or waiting. 
            # Actually, rate limit only triggers on SUCCESSFUL dispatch. Since it wasn't triggered, we're fine.
            
            # 30% drop from old_time, should trigger
            clock.advance(1)
            service.on_price_update("p2", "m2", v1_domain.PriceRecord(clock.now_sec(), 700, True))
            assert len(adapter.sent_messages) == 1

class Testv2_rate_limiting(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v2_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            
            assert dispatcher.dispatch("sub3", "u3", v1_domain.Channel.EMAIL, "msg1") is True
            assert len(adapter.sent_messages) == 1
            
            # Should be rate limited
            assert dispatcher.dispatch("sub3", "u3", v1_domain.Channel.EMAIL, "msg2") is False
            assert len(adapter.sent_messages) == 1

class Testv2_unsupported_channel(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v2_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            
            # Send via SMS but no SMS adapter registered
            assert dispatcher.dispatch("sub4", "u4", v1_domain.Channel.SMS, "msg") is False

# V3 Integrated Tests
class Testv3_integrated_threshold_alert_and_unsubscribe(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v3_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v3_service.InMemoryPriceHistoryStore(retention_seconds=3600, clock=clock)
            service = v3_service.PriceService(store, dispatcher)
            
            sub = v1_domain.PriceAlertSubscription("sub1", "u1", "p1", threshold_price=1000, channel=v1_domain.Channel.EMAIL)
            service.subscribe(sub)
            
            # Initial price above threshold
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1200, True))
            assert len(adapter.sent_messages) == 0
            
            # Price drops below threshold - triggers alert
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 900, True))
            assert len(adapter.sent_messages) == 1
            
            # Price stays below threshold - no new alert (crossing logic)
            clock.advance(70) # past rate limit
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 800, True))
            assert len(adapter.sent_messages) == 1
            
            # Price goes above threshold
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1100, True))
            assert len(adapter.sent_messages) == 1
            
            # Price drops below threshold again - triggers alert
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 950, True))
            assert len(adapter.sent_messages) == 2
            
            # Unsubscribe
            service.unsubscribe("sub1")
            
            # Price drops - no alert
            clock.advance(10)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 850, True))
            assert len(adapter.sent_messages) == 2

class Testv3_integrated_out_of_order_timestamps_and_retention(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v3_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v3_service.InMemoryPriceHistoryStore(retention_seconds=3600, clock=clock)
            service = v3_service.PriceService(store, dispatcher)
            
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1200, True))
            
            # Out of order timestamp (earlier)
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec() - 100, 900, True))
            
            # Current price should still be 1200
            assert store.get_current_price("p1", "m1") == 1200
            
            # Fast forward 2 hours
            clock.advance(7200)
            
            # New update
            service.on_price_update("p1", "m1", v1_domain.PriceRecord(clock.now_sec(), 1100, True))
            
            # Old records should be cleaned up
            assert len(store.get_history("p1", "m1")) == 1
            assert store.get_current_price("p1", "m1") == 1100

class Testv3_integrated_price_collector(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v3_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v3_service.InMemoryPriceHistoryStore(retention_seconds=3600, clock=clock)
            service = v3_service.PriceService(store, dispatcher)
            
            transport = MockTransport()
            collector = v3_collector.PriceCollector(
                price_service=service,
                product_ids=["p1", "missing"],
                merchant_ids=["m1"],
                transport=transport,
                clock=clock
            )
            
            collector.poll()
            
            assert store.get_current_price("p1", "m1") == 1500
            assert store.get_current_price("missing", "m1") is None

class Testv3_integrated_percentage_drop_alert(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v3_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            store = v3_service.InMemoryPriceHistoryStore(retention_seconds=48 * 3600, clock=clock) # Need at least 24h retention
            service = v3_service.PriceService(store, dispatcher)
            
            sub = v1_domain.PriceAlertSubscription("sub2", "u2", "p2", percentage_drop=20.0, channel=v1_domain.Channel.EMAIL)
            service.subscribe(sub)
            
            old_time = clock.now_sec() - (25 * 60 * 60) # 25 hours ago
            service.on_price_update("p2", "m2", v1_domain.PriceRecord(old_time, 1000, True))
            
            # 10% drop, should not trigger
            service.on_price_update("p2", "m2", v1_domain.PriceRecord(clock.now_sec(), 900, True))
            assert len(adapter.sent_messages) == 0
            
            # Wait to reset rate limit for a real test, but we can bypass rate limit logic by sending a different subscription id or waiting. 
            # Actually, rate limit only triggers on SUCCESSFUL dispatch. Since it wasn't triggered, we're fine.
            
            # 30% drop from old_time, should trigger
            clock.advance(1)
            service.on_price_update("p2", "m2", v1_domain.PriceRecord(clock.now_sec(), 700, True))
            assert len(adapter.sent_messages) == 1

class Testv3_integrated_rate_limiting(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v3_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            
            assert dispatcher.dispatch("sub3", "u3", v1_domain.Channel.EMAIL, "msg1") is True
            assert len(adapter.sent_messages) == 1
            
            # Should be rate limited
            assert dispatcher.dispatch("sub3", "u3", v1_domain.Channel.EMAIL, "msg2") is False
            assert len(adapter.sent_messages) == 1

class Testv3_integrated_unsupported_channel(unittest.TestCase):
        def runTest(self):
            clock = MockClock(1000000)
            adapter = MockAdapter()
            dispatcher = v3_dispatcher.RateLimitedDispatcher({v1_domain.Channel.EMAIL: adapter}, clock, rate_limit_window_sec=60)
            
            # Send via SMS but no SMS adapter registered
            assert dispatcher.dispatch("sub4", "u4", v1_domain.Channel.SMS, "msg") is False


# V3 Original Tests
# V3 Tests
class Testv3_deduplication(unittest.TestCase):
        def runTest(self):
            tracker = v3_buffer.OptimizedPriceTracker(window_size=10)
            assert tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1000, 500, True)) is True
            assert tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1000, 500, True)) is False # duplicate
            
            stats = tracker.get_stats("p1", "m1")
            assert stats["moving_average"] == 500.0

class Testv3_moving_average_and_window(unittest.TestCase):
        def runTest(self):
            tracker = v3_buffer.OptimizedPriceTracker(window_size=2)
            tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1000, 100, True))
            tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1001, 200, True))
            
            stats = tracker.get_stats("p1", "m1")
            assert stats["moving_average"] == 150.0
            
            # Push out oldest
            tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1002, 300, True))
            stats = tracker.get_stats("p1", "m1")
            assert stats["moving_average"] == 250.0 # (200 + 300) / 2

class Testv3_all_time_low(unittest.TestCase):
        def runTest(self):
            tracker = v3_buffer.OptimizedPriceTracker(window_size=2)
            tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1000, 500, True))
            tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1001, 200, True))
            tracker.add_tick("p1", "m1", v1_domain.PriceRecord(1002, 800, True))
            
            stats = tracker.get_stats("p1", "m1")
            assert stats["all_time_low"] == 200

class Testv3_thread_safety(unittest.TestCase):
        def runTest(self):
            tracker = v3_buffer.OptimizedPriceTracker(window_size=1000)
            
            def worker():
                for i in range(100):
                    tracker.add_tick("p1", "m1", v1_domain.PriceRecord(i, i * 10, True))
                    
            threads = [threading.Thread(target=worker) for _ in range(10)]
            for t in threads: t.start()
            for t in threads: t.join()
            
            stats = tracker.get_stats("p1", "m1")
            assert stats["all_time_low"] == 0

# substantive change


class TestEverything(unittest.TestCase):
            pass

for name in list(globals().keys()):
            if name.startswith("test_") and callable(globals()[name]):
                func = globals()[name]
                def wrapper(self, f=func):
                    f()
                setattr(TestEverything, name, wrapper)

if __name__ == '__main__':
            unittest.main()
if __name__ == '__main__':    unittest.main()

if __name__ == '__main__':
    unittest.main()
