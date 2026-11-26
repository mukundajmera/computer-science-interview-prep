from collections import deque
from typing import List


class Solution:
    def getFood(self, grid: List[List[str]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        queue = deque()
        seen = set()
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == "*":
                    queue.append((row, col, 0))
                    seen.add((row, col))
        while queue:
            row, col, distance = queue.popleft()
            for row_delta, col_delta in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_row = row + row_delta
                next_col = col + col_delta
                if not (0 <= next_row < rows and 0 <= next_col < cols) or (next_row, next_col) in seen or grid[next_row][next_col] == "X":
                    continue
                if grid[next_row][next_col] == "#":
                    return distance + 1
                seen.add((next_row, next_col))
                queue.append((next_row, next_col, distance + 1))
        return -1
