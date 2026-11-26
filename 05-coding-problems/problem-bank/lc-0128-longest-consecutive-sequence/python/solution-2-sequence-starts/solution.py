from typing import List


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        values = set(nums)
        best = 0
        for num in values:
            if num - 1 in values:
                continue
            length = 1
            next_value = num + 1
            while next_value in values:
                length += 1
                next_value += 1
            best = max(best, length)
        return best
