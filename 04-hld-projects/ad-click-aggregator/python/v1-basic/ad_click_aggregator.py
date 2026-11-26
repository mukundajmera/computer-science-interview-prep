from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, Set, Protocol, Tuple, Optional
from collections import defaultdict

@dataclass
class ClickEvent:
    event_id: str
    event_time: datetime
    campaign_id: str
    ad_group_id: str
    publisher_id: str

@dataclass
class AggregateResult:
    campaign_id: str
    ad_group_id: str
    publisher_id: str
    clicks: int


class AdClickAggregator(Protocol):
    def record_click(self, event: ClickEvent) -> None: ...
    def get_campaign_clicks(self, campaign_id: str, start_time: datetime, end_time: datetime) -> int: ...
    def get_ad_group_clicks(self, ad_group_id: str, start_time: datetime, end_time: datetime) -> int: ...
    def get_publisher_clicks(self, publisher_id: str, start_time: datetime, end_time: datetime) -> int: ...


class InMemoryAdClickAggregator:
    def __init__(self):
        # Stores seen event_ids to ensure idempotency (deduplication)
        self.seen_events: Set[str] = set()
        # Aggregation store: (window_start: datetime, campaign_id: str, ad_group_id: str, publisher_id: str) -> count: int
        # Window size is 1 minute aligned to UTC.
        self.buckets: Dict[Tuple[datetime, str, str, str], int] = defaultdict(int)

    def record_click(self, event: ClickEvent) -> None:
        if not event.event_id or not event.campaign_id or not event.ad_group_id or not event.publisher_id:
            raise ValueError("All dimensions and event_id must be provided and non-empty")
        if not event.event_time:
            raise ValueError("event_time must be provided")

        if event.event_id in self.seen_events:
            return # Deduplicated
        self.seen_events.add(event.event_id)

        # Truncate to the minute boundary
        window_start = event.event_time.replace(second=0, microsecond=0)

        # Ensure UTC if tz-aware, or assume UTC if naive (to be consistent, it's best to stick to UTC)
        if window_start.tzinfo is not None:
             window_start = window_start.astimezone(timezone.utc)
             window_start = window_start.replace(tzinfo=None)

        self.buckets[(window_start, event.campaign_id, event.ad_group_id, event.publisher_id)] += 1

    def _normalize(self, dt: datetime) -> datetime:
        if dt.tzinfo is not None:
             dt = dt.astimezone(timezone.utc)
        return dt.replace(tzinfo=None)

    def get_campaign_clicks(self, campaign_id: str, start_time: datetime, end_time: datetime) -> int:
        total_clicks = 0
        norm_start = self._normalize(start_time)
        norm_end = self._normalize(end_time)

        for (bucket_time, b_campaign_id, _, _), count in self.buckets.items():
            if b_campaign_id == campaign_id and norm_start <= bucket_time < norm_end:
                total_clicks += count

        return total_clicks

    def get_ad_group_clicks(self, ad_group_id: str, start_time: datetime, end_time: datetime) -> int:
        total_clicks = 0
        norm_start = self._normalize(start_time)
        norm_end = self._normalize(end_time)

        for (bucket_time, _, b_ad_group_id, _), count in self.buckets.items():
            if b_ad_group_id == ad_group_id and norm_start <= bucket_time < norm_end:
                total_clicks += count

        return total_clicks

    def get_publisher_clicks(self, publisher_id: str, start_time: datetime, end_time: datetime) -> int:
        total_clicks = 0
        norm_start = self._normalize(start_time)
        norm_end = self._normalize(end_time)

        for (bucket_time, _, _, b_publisher_id), count in self.buckets.items():
            if b_publisher_id == publisher_id and norm_start <= bucket_time < norm_end:
                total_clicks += count

        return total_clicks
