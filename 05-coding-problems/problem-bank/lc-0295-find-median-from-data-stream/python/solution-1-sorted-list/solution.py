from __future__ import annotations

from bisect import insort


class MedianFinder:
    def __init__(self) -> None:
        self.values: list[int] = []

    def addNum(self, num: int) -> None:
        insort(self.values, num)

    def findMedian(self) -> float:
        size = len(self.values)
        middle = size // 2
        if size % 2 == 1:
            return float(self.values[middle])
        return (self.values[middle - 1] + self.values[middle]) / 2.0
