from __future__ import annotations

from collections import deque
from typing import Deque, List, Tuple


class Solution:
    def updateMatrix(self, mat: List[List[int]]) -> List[List[int]]:
        rows = len(mat)
        cols = len(mat[0])
        distance = [[-1] * cols for _ in range(rows)]
        queue: Deque[Tuple[int, int]] = deque()
        for row in range(rows):
            for col in range(cols):
                if mat[row][col] == 0:
                    distance[row][col] = 0
                    queue.append((row, col))
        while queue:
            row, col = queue.popleft()
            for next_row, next_col in ((row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)):
                if next_row < 0 or next_row >= rows or next_col < 0 or next_col >= cols:
                    continue
                if distance[next_row][next_col] != -1:
                    continue
                distance[next_row][next_col] = distance[row][col] + 1
                queue.append((next_row, next_col))
        return distance
