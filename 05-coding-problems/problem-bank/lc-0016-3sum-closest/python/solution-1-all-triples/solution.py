from typing import List


class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        best = nums[0] + nums[1] + nums[2]
        for i in range(len(nums) - 2):
            for j in range(i + 1, len(nums) - 1):
                for k in range(j + 1, len(nums)):
                    total = nums[i] + nums[j] + nums[k]
                    if abs(total - target) < abs(best - target):
                        best = total
        return best
