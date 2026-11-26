from __future__ import annotations

from collections import deque
from typing import Deque, List, Tuple


class Solution:
    def orangesRotting(self, grid: List[List[int]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        queue: Deque[Tuple[int, int]] = deque()
        fresh = 0
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == 2:
                    queue.append((row, col))
                elif grid[row][col] == 1:
                    fresh += 1
        minutes = 0
        while fresh > 0 and queue:
            for _ in range(len(queue)):
                row, col = queue.popleft()
                for next_row, next_col in ((row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)):
                    if next_row < 0 or next_row >= rows or next_col < 0 or next_col >= cols:
                        continue
                    if grid[next_row][next_col] != 1:
                        continue
                    grid[next_row][next_col] = 2
                    fresh -= 1
                    queue.append((next_row, next_col))
            minutes += 1
        return minutes if fresh == 0 else -1
