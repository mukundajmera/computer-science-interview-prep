from __future__ import annotations

from functools import lru_cache
from typing import List


class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        total = sum(nums)
        if total % 2 == 1:
            return False
        target = total // 2

        @lru_cache(maxsize=None)
        def search(index: int, remaining: int) -> bool:
            if remaining == 0:
                return True
            if remaining < 0 or index == len(nums):
                return False
            return search(index + 1, remaining - nums[index]) or search(index + 1, remaining)

        return search(0, target)
