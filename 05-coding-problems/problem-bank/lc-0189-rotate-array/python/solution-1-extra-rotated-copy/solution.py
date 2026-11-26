from typing import List


class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        n = len(nums)
        if n == 0:
            return

        shift = k % n
        rotated = [0] * n
        for index, value in enumerate(nums):
            rotated[(index + shift) % n] = value
        nums[:] = rotated
