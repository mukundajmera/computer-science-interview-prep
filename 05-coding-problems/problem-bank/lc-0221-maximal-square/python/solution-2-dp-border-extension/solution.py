from __future__ import annotations


class Solution:
    def maximalSquare(self, matrix: list[list[str]]) -> int:
        rows = len(matrix)
        cols = len(matrix[0])
        dp = [[0] * (cols + 1) for _ in range(rows + 1)]
        best_side = 0

        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                if matrix[row - 1][col - 1] == "1":
                    dp[row][col] = 1 + min(
                        dp[row - 1][col - 1],
                        dp[row - 1][col],
                        dp[row][col - 1],
                    )
                    best_side = max(best_side, dp[row][col])

        return best_side * best_side
