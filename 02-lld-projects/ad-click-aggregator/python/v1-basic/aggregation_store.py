"""AggregationStore for ad-click-aggregator (v1-basic)."""

from typing import Dict, List, Tuple
from aggregation_key import AggregationKey

class AggregationStore:
    def increment(self, key: AggregationKey, count: int = 1) -> None:
        raise NotImplementedError()

    def get_count(self, key: AggregationKey) -> int:
        raise NotImplementedError()

    def get_all(self) -> Dict[AggregationKey, int]:
        raise NotImplementedError()
