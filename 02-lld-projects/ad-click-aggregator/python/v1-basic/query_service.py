"""QueryService for ad-click-aggregator (v1-basic)."""

from aggregation_store import AggregationStore
from aggregation_key import AggregationKey

class QueryService:
    def __init__(self, store: AggregationStore) -> None:
        self.store = store

    def get_clicks_for_ad(self, ad_id: str, window_start_ms: int) -> int:
        key = AggregationKey(ad_id, window_start_ms)
        return self.store.get_count(key)
