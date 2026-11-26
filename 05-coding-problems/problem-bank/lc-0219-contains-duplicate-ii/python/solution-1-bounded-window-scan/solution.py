from typing import List


class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        for left in range(len(nums)):
            right_limit = min(len(nums) - 1, left + k)
            for right in range(left + 1, right_limit + 1):
                if nums[left] == nums[right]:
                    return True
        return False
