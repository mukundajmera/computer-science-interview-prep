
from typing import List, Protocol


class WindowedTopKService(Protocol):
    def ingest_view(self, video_id: str, timestamp_ms: int) -> None: ...
    def top_k(self, window_key: str, k: int) -> List[str]: ...
