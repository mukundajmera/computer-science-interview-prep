from typing import List


class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        pairs: List[List[int]] = []
        for a in nums1:
            for b in nums2:
                pairs.append([a, b])
        pairs.sort(key=lambda pair: (pair[0] + pair[1], pair[0], pair[1]))
        return pairs[:k]
