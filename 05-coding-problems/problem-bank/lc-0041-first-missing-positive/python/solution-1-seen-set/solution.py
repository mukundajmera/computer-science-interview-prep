from typing import List


class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        seen = {num for num in nums if num > 0}
        candidate = 1
        while candidate in seen:
            candidate += 1
        return candidate
