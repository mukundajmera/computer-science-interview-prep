from __future__ import annotations

from typing import List


class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        total = sum(nums)
        if total % 2 == 1:
            return False
        target = total // 2
        reachable = [False] * (target + 1)
        reachable[0] = True
        for num in nums:
            for current in range(target, num - 1, -1):
                reachable[current] = reachable[current] or reachable[current - num]
        return reachable[target]
