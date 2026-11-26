from __future__ import annotations

from typing import List


class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        result: List[List[int]] = []
        current: List[int] = []

        def backtrack(index: int) -> None:
            if index == len(nums):
                result.append(current.copy())
                return
            backtrack(index + 1)
            current.append(nums[index])
            backtrack(index + 1)
            current.pop()

        backtrack(0)
        return result
