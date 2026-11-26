from __future__ import annotations


class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        total = len(nums1) + len(nums2)
        middle = total // 2
        left = 0
        right = 0
        previous = 0
        current = 0

        for _ in range(middle + 1):
            previous = current
            if right >= len(nums2) or (left < len(nums1) and nums1[left] <= nums2[right]):
                current = nums1[left]
                left += 1
            else:
                current = nums2[right]
                right += 1

        if total % 2 == 1:
            return float(current)
        return (previous + current) / 2.0
