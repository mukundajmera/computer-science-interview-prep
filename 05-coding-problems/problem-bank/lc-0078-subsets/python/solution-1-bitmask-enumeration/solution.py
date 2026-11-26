from __future__ import annotations

from typing import List


class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        result: List[List[int]] = []
        for mask in range(1 << len(nums)):
            subset = [nums[index] for index in range(len(nums)) if mask & (1 << index)]
            result.append(subset)
        return result
