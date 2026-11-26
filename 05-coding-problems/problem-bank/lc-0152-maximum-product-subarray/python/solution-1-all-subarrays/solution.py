from __future__ import annotations

from typing import List


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        best = nums[0]
        for left in range(len(nums)):
            product = 1
            for right in range(left, len(nums)):
                product *= nums[right]
                best = max(best, product)
        return best
