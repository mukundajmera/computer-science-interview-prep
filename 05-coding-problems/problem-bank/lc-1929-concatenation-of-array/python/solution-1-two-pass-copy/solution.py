from typing import List


class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:
        result = [0] * (2 * len(nums))
        for index, value in enumerate(nums):
            result[index] = value
            result[index + len(nums)] = value
        return result
