from typing import List


class Solution:
    def anagramMappings(self, nums1: List[int], nums2: List[int]) -> List[int]:
        used = [False] * len(nums2)
        result = []
        for value in nums1:
            for index, candidate in enumerate(nums2):
                if not used[index] and candidate == value:
                    used[index] = True
                    result.append(index)
                    break
        return result
