from __future__ import annotations


class Solution:
    def minimumTotal(self, triangle: list[list[int]]) -> int:
        dp = [[0] * len(triangle) for _ in range(len(triangle))]
        dp[0][0] = triangle[0][0]

        for row in range(1, len(triangle)):
            for col in range(row + 1):
                best = 10**18
                if col < row:
                    best = min(best, dp[row - 1][col])
                if col > 0:
                    best = min(best, dp[row - 1][col - 1])
                dp[row][col] = best + triangle[row][col]

        return min(dp[-1])
