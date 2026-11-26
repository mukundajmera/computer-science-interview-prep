from typing import List


class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        write = m + n - 1
        left = m - 1
        right = n - 1
        while right >= 0:
            if left >= 0 and nums1[left] > nums2[right]:
                nums1[write] = nums1[left]
                left -= 1
            else:
                nums1[write] = nums2[right]
                right -= 1
            write -= 1
