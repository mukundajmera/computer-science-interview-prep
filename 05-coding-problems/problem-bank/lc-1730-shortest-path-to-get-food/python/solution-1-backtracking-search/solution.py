from typing import List


class Solution:
    def getFood(self, grid: List[List[str]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        best = rows * cols + 1
        start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "*")

        def dfs(row: int, col: int, distance: int) -> None:
            nonlocal best
            if distance >= best or row < 0 or col < 0 or row == rows or col == cols or grid[row][col] == "X":
                return
            if grid[row][col] == "#":
                best = distance
                return
            original = grid[row][col]
            grid[row][col] = "X"
            for row_delta, col_delta in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                dfs(row + row_delta, col + col_delta, distance + 1)
            grid[row][col] = original

        dfs(start[0], start[1], 0)
        return -1 if best == rows * cols + 1 else best
