from bisect import bisect_right
from collections import defaultdict
from typing import DefaultDict, List, Tuple


class TimeMap:
    def __init__(self) -> None:
        self.values: DefaultDict[str, List[Tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.values[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        history = self.values.get(key, [])
        index = bisect_right(history, (timestamp, chr(255))) - 1
        return history[index][1] if index >= 0 else ""
