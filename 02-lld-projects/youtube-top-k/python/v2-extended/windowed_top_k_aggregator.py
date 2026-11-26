from typing import Protocol


class WindowedTopKAggregator(Protocol):
    def ingest(self, video_id: str, event_time_ms: int) -> None: ...
