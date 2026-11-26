from typing import List


class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        last_seen = {}
        for index, value in enumerate(nums):
            previous = last_seen.get(value)
            if previous is not None and index - previous <= k:
                return True
            last_seen[value] = index
        return False
