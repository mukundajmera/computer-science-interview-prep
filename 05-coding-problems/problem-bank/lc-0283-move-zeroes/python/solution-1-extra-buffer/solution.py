from typing import List


class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        non_zeroes = [num for num in nums if num != 0]
        nums[:len(non_zeroes)] = non_zeroes
        for index in range(len(non_zeroes), len(nums)):
            nums[index] = 0
