from typing import List, Protocol


class TopKQueryService(Protocol):
    def top_k(self, window_key: str, k: int) -> List[str]: ...
