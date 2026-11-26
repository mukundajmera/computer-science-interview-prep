from __future__ import annotations


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.clock = 0
        self.entries: dict[int, list[int]] = {}

    def get(self, key: int) -> int:
        if key not in self.entries:
            return -1
        self._touch(key)
        return self.entries[key][0]

    def put(self, key: int, value: int) -> None:
        if key in self.entries:
            self.entries[key][0] = value
            self._touch(key)
            return
        if len(self.entries) == self.capacity:
            oldest_key = min(self.entries, key=lambda item: self.entries[item][1])
            del self.entries[oldest_key]
        self.clock += 1
        self.entries[key] = [value, self.clock]

    def _touch(self, key: int) -> None:
        self.clock += 1
        self.entries[key][1] = self.clock
