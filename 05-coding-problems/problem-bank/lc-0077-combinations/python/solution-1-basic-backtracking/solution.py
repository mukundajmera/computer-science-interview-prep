from typing import List


class Solution:
    def combine(self, n: int, k: int) -> List[List[int]]:
        result: List[List[int]] = []
        path: List[int] = []

        def backtrack(start: int) -> None:
            if len(path) == k:
                result.append(path.copy())
                return
            for value in range(start, n + 1):
                path.append(value)
                backtrack(value + 1)
                path.pop()

        backtrack(1)
        return result
