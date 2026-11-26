from typing import List


class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:
        return [nums[index % len(nums)] for index in range(2 * len(nums))]
