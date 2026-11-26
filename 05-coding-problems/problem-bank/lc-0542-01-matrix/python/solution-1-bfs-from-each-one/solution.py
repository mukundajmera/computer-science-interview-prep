from __future__ import annotations

from collections import deque
from typing import Deque, List, Tuple


class Solution:
    def updateMatrix(self, mat: List[List[int]]) -> List[List[int]]:
        rows = len(mat)
        cols = len(mat[0])

        def nearest_zero(start_row: int, start_col: int) -> int:
            if mat[start_row][start_col] == 0:
                return 0
            seen = [[False] * cols for _ in range(rows)]
            queue: Deque[Tuple[int, int, int]] = deque([(start_row, start_col, 0)])
            seen[start_row][start_col] = True
            while queue:
                row, col, distance = queue.popleft()
                for next_row, next_col in ((row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)):
                    if next_row < 0 or next_row >= rows or next_col < 0 or next_col >= cols:
                        continue
                    if seen[next_row][next_col]:
                        continue
                    if mat[next_row][next_col] == 0:
                        return distance + 1
                    seen[next_row][next_col] = True
                    queue.append((next_row, next_col, distance + 1))
            return 0

        return [[nearest_zero(row, col) for col in range(cols)] for row in range(rows)]
