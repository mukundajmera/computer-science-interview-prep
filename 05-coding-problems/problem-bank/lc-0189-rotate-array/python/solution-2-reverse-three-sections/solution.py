from typing import List


class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        if len(nums) == 0:
            return

        shift = k % len(nums)
        if shift == 0:
            return

        self._reverse(nums, 0, len(nums) - 1)
        self._reverse(nums, 0, shift - 1)
        self._reverse(nums, shift, len(nums) - 1)

    def _reverse(self, nums: List[int], left: int, right: int) -> None:
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
