from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        visited = [[False] * cols for _ in range(rows)]
        islands = 0
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == "1" and not visited[row][col]:
                    islands += 1
                    self._visit(grid, visited, row, col)
        return islands

    def _visit(self, grid: List[List[str]], visited: List[List[bool]], row: int, col: int) -> None:
        if row < 0 or row == len(grid) or col < 0 or col == len(grid[0]):
            return
        if visited[row][col] or grid[row][col] != "1":
            return
        visited[row][col] = True
        self._visit(grid, visited, row + 1, col)
        self._visit(grid, visited, row - 1, col)
        self._visit(grid, visited, row, col + 1)
        self._visit(grid, visited, row, col - 1)
