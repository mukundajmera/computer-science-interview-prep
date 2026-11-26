from __future__ import annotations

from typing import List


class Solution:
    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:
        return sorted(points, key=lambda point: point[0] * point[0] + point[1] * point[1])[:k]
