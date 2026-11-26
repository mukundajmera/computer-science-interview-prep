from __future__ import annotations

import random


class RandomizedSet:
    def __init__(self) -> None:
        self.values: set[int] = set()

    def insert(self, val: int) -> bool:
        if val in self.values:
            return False
        self.values.add(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.values:
            return False
        self.values.remove(val)
        return True

    def getRandom(self) -> int:
        snapshot = list(self.values)
        return random.choice(snapshot)
