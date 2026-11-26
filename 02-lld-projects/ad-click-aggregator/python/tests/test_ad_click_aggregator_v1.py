import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

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

from ad_click_aggregator import AdClickAggregator
from in_memory_aggregation_store import InMemoryAggregationStore
from query_service import QueryService
from click_event import ClickEvent



# Tests deliberately select this version in both languages, compile independently and include normal/edge/rollback fixtures without external network or uncontrolled wall-clock waits.
class TestV1(unittest.TestCase):
    def test_v1_sanity(self) -> None:
        store = InMemoryAggregationStore()
        ad_click_aggregator = AdClickAggregator(store, window_size_ms=60000)
        query = QueryService(store)
        
        ad_click_aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))
        ad_click_aggregator.ingest(ClickEvent("e2", "ad1", "u2", 2000))
        ad_click_aggregator.ingest(ClickEvent("e3", "ad1", "u3", 65000))
        
        self.assertEqual(query.get_clicks_for_ad("ad1", 0), 2)
        self.assertEqual(query.get_clicks_for_ad("ad1", 60000), 1)
        self.assertEqual(query.get_clicks_for_ad("ad2", 0), 0)

    def test_v1_deduplication(self) -> None:
        store = InMemoryAggregationStore()
        ad_click_aggregator = AdClickAggregator(store, window_size_ms=60000)
        query = QueryService(store)
        
        # Ingest same event ID multiple times
        ad_click_aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))
        ad_click_aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))
        ad_click_aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))
        
        # Should only be counted once
        self.assertEqual(query.get_clicks_for_ad("ad1", 0), 1)

    def test_v1_window_boundaries(self) -> None:
        store = InMemoryAggregationStore()
        ad_click_aggregator = AdClickAggregator(store, window_size_ms=60000)
        query = QueryService(store)

        ad_click_aggregator.ingest(ClickEvent("e1", "ad1", "u1", 0))
        ad_click_aggregator.ingest(ClickEvent("e2", "ad1", "u1", 59999))
        ad_click_aggregator.ingest(ClickEvent("e3", "ad1", "u1", 60000))

        self.assertEqual(query.get_clicks_for_ad("ad1", 0), 2)
        self.assertEqual(query.get_clicks_for_ad("ad1", 60000), 1)

    def test_v1_rollback_on_store_failure(self) -> None:
        class FailingStore:
            def increment(self, key, count=1):
                raise RuntimeError("Store failure")
            def get_count(self, key):
                return 0
            def get_all(self):
                return {}
        
        ad_click_aggregator = AdClickAggregator(FailingStore(), window_size_ms=60000)
        event = ClickEvent("e1", "ad1", "u1", 1000)

        with self.assertRaises(RuntimeError):
            ad_click_aggregator.ingest(event)

        # The duplicate event should fail again instead of being deduplicated.
        with self.assertRaises(RuntimeError):
            ad_click_aggregator.ingest(event)


    def test_v1_out_of_order_and_late_events(self) -> None:
        store = InMemoryAggregationStore()
        ad_click_aggregator = AdClickAggregator(store, window_size_ms=60000)
        query = QueryService(store)
        
        # Out-of-order events
        ad_click_aggregator.ingest(ClickEvent("e3", "ad1", "u1", 65000))
        ad_click_aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))
        ad_click_aggregator.ingest(ClickEvent("e4", "ad1", "u1", 125000))
        ad_click_aggregator.ingest(ClickEvent("e2", "ad1", "u1", 2000))
        
        # Window sizes are exactly determined by event timestamp
        self.assertEqual(query.get_clicks_for_ad("ad1", 0), 2)
        self.assertEqual(query.get_clicks_for_ad("ad1", 60000), 1)
        self.assertEqual(query.get_clicks_for_ad("ad1", 120000), 1)

    def test_v1_invalid_payloads(self) -> None:
        store = InMemoryAggregationStore()
        ad_click_aggregator = AdClickAggregator(store, window_size_ms=60000)
        
        with self.assertRaises(ValueError):
            ad_click_aggregator.ingest(ClickEvent("", "ad1", "u1", 1000))
        
        with self.assertRaises(ValueError):
            ad_click_aggregator.ingest(ClickEvent("e1", "", "u1", 1000))
            
        with self.assertRaises(ValueError):
            ad_click_aggregator.ingest(None)

if __name__ == "__main__":
    unittest.main()
