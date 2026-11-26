from typing import List


class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        result: List[List[int]] = []
        path: List[int] = []

        def backtrack(start: int, remaining: int) -> None:
            if remaining == 0:
                result.append(path.copy())
                return
            if start == len(candidates) or remaining < candidates[start]:
                return
            path.append(candidates[start])
            backtrack(start, remaining - candidates[start])
            path.pop()
            backtrack(start + 1, remaining)

        backtrack(0, target)
        return result
