"""AdClickAggregator for ad-click-aggregator (v2-extended)."""

import time
from click_event import ClickEvent
from aggregation_key import AggregationKey
from aggregation_store import AggregationStore
from event_deduplicator import EventDeduplicator
from window_strategy import WindowStrategy
from fraud_rule import FraudRule

class AdClickAggregator:
    def __init__(self, store: AggregationStore, deduplicator: EventDeduplicator, window_strategy: WindowStrategy, fraud_rule: FraudRule) -> None:
        self.store = store
        self.deduplicator = deduplicator
        self.window_strategy = window_strategy
        self.fraud_rule = fraud_rule

    def ingest(self, event: ClickEvent, processing_time: int = None) -> None:
        if not event or not event.event_id or not event.ad_id or not event.user_id:
            raise ValueError("Empty input and invalid event payloads fail predictably")
            
        if processing_time is None:
            processing_time = int(time.time() * 1000)
            
        if processing_time - event.timestamp > 300000:
            return
            
        if self.fraud_rule.is_fraud(event.user_id):
            return
            
        if self.deduplicator.is_duplicate(event.event_id):
            return
            
        windows = self.window_strategy.get_overlapping_windows(event.timestamp)
        for window_start in windows:
            key = AggregationKey(event.ad_id, window_start)
            self.store.increment(key, 1)
