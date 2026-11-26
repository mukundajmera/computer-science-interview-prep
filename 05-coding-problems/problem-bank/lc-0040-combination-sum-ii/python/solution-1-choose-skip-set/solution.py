from typing import List


class Solution:
    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        rows = set()

        def backtrack(index: int, remaining: int, path: List[int]) -> None:
            if remaining == 0:
                rows.add(tuple(path))
                return
            if index == len(candidates) or remaining < 0:
                return
            path.append(candidates[index])
            backtrack(index + 1, remaining - candidates[index], path)
            path.pop()
            backtrack(index + 1, remaining, path)

        backtrack(0, target, [])
        return [list(row) for row in rows]
