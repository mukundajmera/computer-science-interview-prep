from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        islands = 0
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == "1":
                    islands += 1
                    self._sink(grid, row, col)
        return islands

    def _sink(self, grid: List[List[str]], row: int, col: int) -> None:
        if row < 0 or row == len(grid) or col < 0 or col == len(grid[0]) or grid[row][col] != "1":
            return
        grid[row][col] = "0"
        self._sink(grid, row + 1, col)
        self._sink(grid, row - 1, col)
        self._sink(grid, row, col + 1)
        self._sink(grid, row, col - 1)
