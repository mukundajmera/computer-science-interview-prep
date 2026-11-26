from typing import List


class Solution:
    def permuteUnique(self, nums: List[int]) -> List[List[int]]:
        rows = set()

        def permute(index: int) -> None:
            if index == len(nums):
                rows.add(tuple(nums))
                return
            for i in range(index, len(nums)):
                nums[index], nums[i] = nums[i], nums[index]
                permute(index + 1)
                nums[index], nums[i] = nums[i], nums[index]

        permute(0)
        return [list(row) for row in rows]
