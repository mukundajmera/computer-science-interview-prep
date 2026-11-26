from typing import List


class Solution:
    def countElements(self, arr: List[int]) -> int:
        values = set(arr)
        return sum(1 for value in arr if value + 1 in values)
