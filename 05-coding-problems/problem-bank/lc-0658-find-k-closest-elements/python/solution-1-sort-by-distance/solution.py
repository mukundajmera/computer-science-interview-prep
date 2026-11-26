from typing import List


class Solution:
    def findClosestElements(self, arr: List[int], k: int, x: int) -> List[int]:
        closest = sorted(arr, key=lambda value: (abs(value - x), value))[:k]
        return sorted(closest)
