from typing import List


class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        low = 1
        high = len(nums) - 1
        while low < high:
            mid = low + (high - low) // 2
            count = sum(1 for value in nums if value <= mid)
            if count > mid:
                high = mid
            else:
                low = mid + 1
        return low
