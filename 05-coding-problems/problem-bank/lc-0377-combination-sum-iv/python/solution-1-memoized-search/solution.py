from functools import lru_cache
from typing import List


class Solution:
    def combinationSum4(self, nums: List[int], target: int) -> int:
        @lru_cache(maxsize=None)
        def count(remaining: int) -> int:
            if remaining == 0:
                return 1
            if remaining < 0:
                return 0
            return sum(count(remaining - value) for value in nums)

        return count(target)
