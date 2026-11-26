from __future__ import annotations


class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        if len(nums1) > len(nums2):
            return self.findMedianSortedArrays(nums2, nums1)

        total = len(nums1) + len(nums2)
        left_size = (total + 1) // 2
        low = 0
        high = len(nums1)

        while low <= high:
            cut1 = (low + high) // 2
            cut2 = left_size - cut1

            left1 = float("-inf") if cut1 == 0 else nums1[cut1 - 1]
            right1 = float("inf") if cut1 == len(nums1) else nums1[cut1]
            left2 = float("-inf") if cut2 == 0 else nums2[cut2 - 1]
            right2 = float("inf") if cut2 == len(nums2) else nums2[cut2]

            if left1 <= right2 and left2 <= right1:
                if total % 2 == 1:
                    return float(max(left1, left2))
                return (max(left1, left2) + min(right1, right2)) / 2.0
            if left1 > right2:
                high = cut1 - 1
            else:
                low = cut1 + 1

        raise ValueError("input arrays must be sorted")
