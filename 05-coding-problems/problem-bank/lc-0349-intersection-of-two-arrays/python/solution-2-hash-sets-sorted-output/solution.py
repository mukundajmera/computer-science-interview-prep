from typing import List


class Solution:
    def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
        first = set(nums1)
        shared = {value for value in nums2 if value in first}
        return sorted(shared)
