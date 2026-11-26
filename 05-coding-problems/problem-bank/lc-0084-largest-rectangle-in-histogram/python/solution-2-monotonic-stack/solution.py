from __future__ import annotations

from typing import List


class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        stack: list[int] = []
        best = 0
        for index in range(len(heights) + 1):
            current_height = 0 if index == len(heights) else heights[index]
            while stack and current_height < heights[stack[-1]]:
                height = heights[stack.pop()]
                left_boundary = stack[-1] if stack else -1
                best = max(best, height * (index - left_boundary - 1))
            stack.append(index)
        return best
