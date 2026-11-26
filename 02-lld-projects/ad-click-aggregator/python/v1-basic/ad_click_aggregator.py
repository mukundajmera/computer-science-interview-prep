"""AdClickAggregator for ad-click-aggregator (v1-basic)."""

from click_event import ClickEvent
from aggregation_key import AggregationKey
from aggregation_store import AggregationStore

import hashlib
from typing import Set

class SimpleBloomFilter:
    def __init__(self, size: int = 10000):
        self.size = size
        self.bit_array = [False] * size

    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.sha256(f"{item}{seed}".encode('utf-8')).hexdigest()
        return int(h, 16) % self.size

    def add(self, item: str) -> None:
        self.bit_array[self._hash(item, 1)] = True
        self.bit_array[self._hash(item, 2)] = True
        self.bit_array[self._hash(item, 3)] = True

    def might_contain(self, item: str) -> bool:
        return (self.bit_array[self._hash(item, 1)] and
                self.bit_array[self._hash(item, 2)] and
                self.bit_array[self._hash(item, 3)])

class AdClickAggregator:
    def __init__(self, store: AggregationStore, window_size_ms: int = 60000) -> None:
        self.store = store
        self.window_size_ms = window_size_ms
        self.bloom_filter = SimpleBloomFilter()
        self.exact_seen_events: Set[str] = set()

    def ingest(self, event: ClickEvent) -> None:
        # empty input and invalid event payloads fail predictably
        if not event or not event.event_id or not event.ad_id:
            raise ValueError("Invalid event payload")

        event_id = event.event_id
        # Duplicate event IDs affect billing aggregates exactly once; probabilistic filters only accelerate an exact deduplication check.
        if self.bloom_filter.might_contain(event_id) and event_id in self.exact_seen_events:
            return
        
        # Window-boundary, late-event and out-of-order timestamp examples state processing-time/event-time policy
        window_start_ms = (event.timestamp // self.window_size_ms) * self.window_size_ms
        key = AggregationKey(event.ad_id, window_start_ms)
        self.store.increment(key, 1)
        
        self.bloom_filter.add(event_id)
        self.exact_seen_events.add(event_id)
