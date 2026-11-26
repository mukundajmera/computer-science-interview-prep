from collections import defaultdict, deque
from typing import Deque, Dict, List


class Solution:
    def anagramMappings(self, nums1: List[int], nums2: List[int]) -> List[int]:
        positions: Dict[int, Deque[int]] = defaultdict(deque)
        for index, value in enumerate(nums2):
            positions[value].append(index)
        return [positions[value].popleft() for value in nums1]
