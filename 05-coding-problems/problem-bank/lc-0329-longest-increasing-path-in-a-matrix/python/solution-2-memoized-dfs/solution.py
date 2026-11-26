from typing import List


class Solution:
    def longestIncreasingPath(self, matrix: List[List[int]]) -> int:
        rows = len(matrix)
        cols = len(matrix[0])
        memo = [[0] * cols for _ in range(rows)]

        def dfs(row: int, col: int) -> int:
            if memo[row][col]:
                return memo[row][col]
            best = 1
            for row_delta, col_delta in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_row = row + row_delta
                next_col = col + col_delta
                if 0 <= next_row < rows and 0 <= next_col < cols and matrix[next_row][next_col] > matrix[row][col]:
                    best = max(best, 1 + dfs(next_row, next_col))
            memo[row][col] = best
            return best

        return max(dfs(row, col) for row in range(rows) for col in range(cols))
