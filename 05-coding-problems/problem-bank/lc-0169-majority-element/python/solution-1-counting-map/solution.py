from typing import Dict, List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        counts: Dict[int, int] = {}
        threshold = len(nums) // 2
        for value in nums:
            counts[value] = counts.get(value, 0) + 1
            if counts[value] > threshold:
                return value
        return nums[0]
