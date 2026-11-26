from typing import List


class Solution:
    def replaceElements(self, arr: List[int]) -> List[int]:
        result = [0] * len(arr)
        best = -1
        for index in range(len(arr) - 1, -1, -1):
            result[index] = best
            best = max(best, arr[index])
        return result
