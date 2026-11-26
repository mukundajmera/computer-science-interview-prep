from __future__ import annotations

from typing import List


class Solution:
    def orangesRotting(self, grid: List[List[int]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        fresh = sum(value == 1 for row in grid for value in row)
        minutes = 0
        while fresh > 0:
            next_wave: list[tuple[int, int]] = []
            for row in range(rows):
                for col in range(cols):
                    if grid[row][col] != 1:
                        continue
                    for nr, nc in ((row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)):
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 2:
                            next_wave.append((row, col))
                            break
            if not next_wave:
                return -1
            for row, col in next_wave:
                if grid[row][col] == 1:
                    grid[row][col] = 2
                    fresh -= 1
            minutes += 1
        return minutes
