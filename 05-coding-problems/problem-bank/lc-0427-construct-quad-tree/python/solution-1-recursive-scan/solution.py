from __future__ import annotations

from typing import List, Optional


class Solution:
    def construct(self, grid: List[List[int]]) -> Optional[Node]:
        def build(row: int, col: int, size: int) -> Node:
            first = grid[row][col]
            uniform = True
            for r in range(row, row + size):
                for c in range(col, col + size):
                    if grid[r][c] != first:
                        uniform = False
                        break
                if not uniform:
                    break
            if uniform:
                return Node(first == 1, True)

            half = size // 2
            return Node(
                True,
                False,
                build(row, col, half),
                build(row, col + half, half),
                build(row + half, col, half),
                build(row + half, col + half, half),
            )

        return build(0, 0, len(grid))
