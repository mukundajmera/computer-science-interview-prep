from __future__ import annotations


class Solution:
    def minimumTotal(self, triangle: list[list[int]]) -> int:
        costs = triangle[-1][:]
        for row in range(len(triangle) - 2, -1, -1):
            for col in range(row + 1):
                costs[col] = triangle[row][col] + min(costs[col], costs[col + 1])
        return costs[0]
