from typing import List


class Solution:
    def canJump(self, nums: List[int]) -> bool:
        reachable = [False] * len(nums)
        reachable[0] = True
        for target in range(1, len(nums)):
            for start in range(target):
                if reachable[start] and start + nums[start] >= target:
                    reachable[target] = True
                    break
        return reachable[-1]
