from typing import List


class Solution:
    def replaceElements(self, arr: List[int]) -> List[int]:
        result = []
        for index in range(len(arr)):
            result.append(max(arr[index + 1:], default=-1))
        return result
