from collections import defaultdict
from typing import DefaultDict, List, Tuple


class TimeMap:
    def __init__(self) -> None:
        self.values: DefaultDict[str, List[Tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.values[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        for seen_at, value in reversed(self.values.get(key, [])):
            if seen_at <= timestamp:
                return value
        return ""
