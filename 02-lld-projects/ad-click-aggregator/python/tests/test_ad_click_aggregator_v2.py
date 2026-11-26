import sys
import os
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

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

from in_memory_aggregation_store import InMemoryAggregationStore
from query_service import QueryService
from click_event import ClickEvent
from ad_click_aggregator import AdClickAggregator
from event_deduplicator import EventDeduplicator
from window_strategy import WindowStrategy
from fraud_rule import FraudRule

class TestV2(unittest.TestCase):
    def test_v2_sanity(self) -> None:
        store = InMemoryAggregationStore()
        deduplicator = EventDeduplicator()
        window_strategy = WindowStrategy(window_size_ms=60000, slide_step_ms=10000)
        fraud_rule = FraudRule()
        
        aggregator = AdClickAggregator(store, deduplicator, window_strategy, fraud_rule)
        query = QueryService(store)
        
        # Normal ingest
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000), processing_time=1000)
        
        # Duplicate event on same ad
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 2000), processing_time=2000)
        
        # Fraud user
        aggregator.ingest(ClickEvent("e3", "ad1", "fraud_user", 3000), processing_time=3000)
        
        # Different user
        aggregator.ingest(ClickEvent("e4", "ad1", "u2", 4000), processing_time=4000)
        
        self.assertEqual(query.get_clicks_for_ad("ad1", 0), 2)
        
    def test_empty_and_invalid_payloads(self) -> None:
        store = InMemoryAggregationStore()
        deduplicator = EventDeduplicator()
        window_strategy = WindowStrategy(window_size_ms=60000, slide_step_ms=10000)
        fraud_rule = FraudRule()
        
        aggregator = AdClickAggregator(store, deduplicator, window_strategy, fraud_rule)
        
        with self.assertRaises(ValueError):
            aggregator.ingest(ClickEvent("", "ad1", "u1", 1000))
        
        with self.assertRaises(ValueError):
            aggregator.ingest(ClickEvent("e1", "", "u1", 1000))
            
        with self.assertRaises(ValueError):
            aggregator.ingest(ClickEvent("e1", "ad1", "", 1000))

    def test_window_boundary_and_late_events(self) -> None:
        store = InMemoryAggregationStore()
        deduplicator = EventDeduplicator()
        window_strategy = WindowStrategy(window_size_ms=60000, slide_step_ms=60000)
        fraud_rule = FraudRule()
        
        aggregator = AdClickAggregator(store, deduplicator, window_strategy, fraud_rule)
        query = QueryService(store)
        
        # Boundary inclusion
        aggregator.ingest(ClickEvent("e1", "ad1", "u1", 60000), processing_time=60000)
        
        # Out-of-order acceptance
        aggregator.ingest(ClickEvent("e2", "ad1", "u2", 30000), processing_time=120000)
        
        # Late-event rejection
        aggregator.ingest(ClickEvent("e3", "ad1", "u3", 30000), processing_time=330001)
        
        # e2 goes to 0 bucket, e1 goes to 60000 bucket, e3 is rejected
        self.assertEqual(query.get_clicks_for_ad("ad1", 0), 1)
        self.assertEqual(query.get_clicks_for_ad("ad1", 60000), 1)

if __name__ == "__main__":
    unittest.main()
