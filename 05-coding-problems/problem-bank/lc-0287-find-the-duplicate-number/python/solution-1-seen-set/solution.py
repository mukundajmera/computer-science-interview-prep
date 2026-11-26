from typing import List, Set


class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        seen: Set[int] = set()
        for value in nums:
            if value in seen:
                return value
            seen.add(value)
        return -1
