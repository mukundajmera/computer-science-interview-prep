from typing import List


class Solution:
    def maxArea(self, height: List[int]) -> int:
        best = 0
        for left in range(len(height)):
            for right in range(left + 1, len(height)):
                area = (right - left) * min(height[left], height[right])
                best = max(best, area)
        return best
