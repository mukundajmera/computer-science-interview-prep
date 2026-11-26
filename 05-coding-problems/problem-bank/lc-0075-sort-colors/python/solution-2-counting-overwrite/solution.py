from typing import List


class Solution:
    def sortColors(self, nums: List[int]) -> None:
        counts = [0, 0, 0]
        for num in nums:
            counts[num] += 1
        index = 0
        for color, count in enumerate(counts):
            for _ in range(count):
                nums[index] = color
                index += 1
