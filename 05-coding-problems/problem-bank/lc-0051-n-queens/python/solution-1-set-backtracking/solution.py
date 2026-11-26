from typing import List, Set


class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        result: List[List[str]] = []
        queens = [-1] * n
        cols: Set[int] = set()
        diag: Set[int] = set()
        anti: Set[int] = set()

        def render() -> List[str]:
            return ["." * col + "Q" + "." * (n - col - 1) for col in queens]

        def backtrack(row: int) -> None:
            if row == n:
                result.append(render())
                return
            for col in range(n):
                if col in cols or row - col in diag or row + col in anti:
                    continue
                queens[row] = col
                cols.add(col)
                diag.add(row - col)
                anti.add(row + col)
                backtrack(row + 1)
                cols.remove(col)
                diag.remove(row - col)
                anti.remove(row + col)

        backtrack(0)
        return result
