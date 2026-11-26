"""AggregationKey for ad-click-aggregator (v1-basic)."""


class AggregationKey:
    def __init__(self, ad_id: str, window_start_ms: int) -> None:
        self.ad_id = ad_id
        self.window_start_ms = window_start_ms

    def __hash__(self) -> int:
        return hash((self.ad_id, self.window_start_ms))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AggregationKey):
            return False
        return self.ad_id == other.ad_id and self.window_start_ms == other.window_start_ms
