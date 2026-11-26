"""InMemoryAggregationStore for ad-click-aggregator (v1-basic)."""
from typing import Dict
from aggregation_store import AggregationStore
from aggregation_key import AggregationKey


class InMemoryAggregationStore(AggregationStore):
    def __init__(self) -> None:
        self.counts: Dict[AggregationKey, int] = {}

    def increment(self, key: AggregationKey, count: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + count

    def get_count(self, key: AggregationKey) -> int:
        return self.counts.get(key, 0)

    def get_all(self) -> Dict[AggregationKey, int]:
        return dict(self.counts)
