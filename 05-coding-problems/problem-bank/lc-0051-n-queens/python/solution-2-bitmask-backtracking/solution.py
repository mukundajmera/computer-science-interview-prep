from typing import List


class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        result: List[List[str]] = []
        queens = [-1] * n
        full = (1 << n) - 1

        def render() -> List[str]:
            return ["." * col + "Q" + "." * (n - col - 1) for col in queens]

        def backtrack(row: int, cols: int, diag: int, anti: int) -> None:
            if row == n:
                result.append(render())
                return
            available = full & ~(cols | diag | anti)
            while available:
                bit = available & -available
                available -= bit
                queens[row] = bit.bit_length() - 1
                backtrack(row + 1, cols | bit, (diag | bit) << 1, (anti | bit) >> 1)

        backtrack(0, 0, 0, 0)
        return result
