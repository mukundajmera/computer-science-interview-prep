from typing import List


class Solution:
    def countElements(self, arr: List[int]) -> int:
        total = 0
        for value in arr:
            if any(candidate == value + 1 for candidate in arr):
                total += 1
        return total
