import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

for module_name in [
    'ad_click_aggregator',
    'click_event',
    'aggregation_key',
    'aggregation_store',
    'in_memory_aggregation_store',
    'query_service',
    'event_deduplicator',
    'window_strategy',
    'fraud_rule',
    'sharded_state_store',
    'watermark_manager',
    'late_event_handler',
    'partition_router',
]:
    sys.modules.pop(module_name, None)

from click_event import ClickEvent
from aggregation_key import AggregationKey
from sharded_state_store import ShardedStateStore
from watermark_manager import WatermarkManager
from late_event_handler import LateEventHandler
from window_strategy import WindowStrategy
from ad_click_aggregator import AdClickAggregator



class TestV3(unittest.TestCase):
    def test_v3_sanity(self) -> None:
        store = ShardedStateStore(num_partitions=4)
        watermark_manager = WatermarkManager()
        late_handler = LateEventHandler(max_lateness_ms=5000)
        window_strategy = WindowStrategy(window_size_ms=60000, slide_step_ms=10000)
        
        aggregator = AdClickAggregator(store, watermark_manager, late_handler, window_strategy)
        
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 10000))
        
        # Late event (older than watermark - 5000) -> should be dropped
        aggregator.ingest(ClickEvent("e2", "ad1", "u2", 4000)) 
        
        # In-time event -> should be processed
        aggregator.ingest(ClickEvent("e3", "ad1", "u3", 8000))
        
        key = AggregationKey("ad1", 0)
        self.assertEqual(store.get_count(key), 2)

    def test_v3_deduplication_and_validation(self) -> None:
        from event_deduplicator import EventDeduplicator
        store = ShardedStateStore(num_partitions=4)
        watermark_manager = WatermarkManager()
        late_handler = LateEventHandler(max_lateness_ms=5000)
        window_strategy = WindowStrategy(window_size_ms=60000, slide_step_ms=10000)
        deduplicator = EventDeduplicator()
        
        aggregator = AdClickAggregator(store, watermark_manager, late_handler, window_strategy, deduplicator)
        
        # Invalid input fails predictably
        with self.assertRaises(ValueError):
            aggregator.ingest(ClickEvent("", "ad1", "u1", 10000))

        # Deduplication check exactly once
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 10000))
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 10000)) # Duplicate
        
        key = AggregationKey("ad1", 0)
        self.assertEqual(store.get_count(key), 1)

    def test_v3_processing_time_policy(self) -> None:
        store = ShardedStateStore(num_partitions=4)
        watermark_manager = WatermarkManager()
        late_handler = LateEventHandler(max_lateness_ms=5000)
        window_strategy = WindowStrategy(window_size_ms=60000, slide_step_ms=10000)
        
        aggregator = AdClickAggregator(store, watermark_manager, late_handler, window_strategy)
        
        # processing-time vs event-time policy
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000), processing_time=400000)
        key = AggregationKey("ad1", 0)
        self.assertEqual(store.get_count(key), 0)

if __name__ == "__main__":
    unittest.main()