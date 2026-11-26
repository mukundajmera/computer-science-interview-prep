from typing import Set


class CardinalityGuard:
    def __init__(self, max_series: int) -> None:
        self.max_series = max_series
        self._seen_series: Set[str] = set()

    def accept(self, series_key: str) -> bool:
        if series_key in self._seen_series:
            return True
        if len(self._seen_series) >= self.max_series:
            return False
        self._seen_series.add(series_key)
        return True
