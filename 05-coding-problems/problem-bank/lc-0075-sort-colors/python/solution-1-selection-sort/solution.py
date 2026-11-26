from typing import List


class Solution:
    def sortColors(self, nums: List[int]) -> None:
        for index in range(len(nums)):
            smallest = index
            for scan in range(index + 1, len(nums)):
                if nums[scan] < nums[smallest]:
                    smallest = scan
            nums[index], nums[smallest] = nums[smallest], nums[index]
