from typing import List


class Solution:
    def search(self, nums: List[int], target: int) -> bool:
        return any(value == target for value in nums)
