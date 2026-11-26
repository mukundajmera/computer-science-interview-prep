from typing import List


class Solution:
    def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
        left = sorted(nums1)
        right = sorted(nums2)
        shared = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            left_value = left[i]
            right_value = right[j]
            if left_value == right_value:
                shared.append(left_value)
                while i < len(left) and left[i] == left_value:
                    i += 1
                while j < len(right) and right[j] == right_value:
                    j += 1
            elif left_value < right_value:
                while i < len(left) and left[i] == left_value:
                    i += 1
            else:
                while j < len(right) and right[j] == right_value:
                    j += 1
        return shared
