from typing import List


class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        seen = set()
        for value in nums:
            if value in seen:
                seen.remove(value)
            else:
                seen.add(value)
        return next(iter(seen))
