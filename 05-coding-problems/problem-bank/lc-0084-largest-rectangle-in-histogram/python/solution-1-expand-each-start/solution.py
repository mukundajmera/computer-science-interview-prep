from __future__ import annotations

from typing import List


class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        best = 0
        for left in range(len(heights)):
            min_height = float("inf")
            for right in range(left, len(heights)):
                min_height = min(min_height, heights[right])
                best = max(best, int(min_height) * (right - left + 1))
        return best
