from __future__ import annotations

from typing import List, Optional


class Solution:
    def construct(self, grid: List[List[int]]) -> Optional[Node]:
        n = len(grid)
        prefix = [[0] * (n + 1) for _ in range(n + 1)]
        for row in range(n):
            for col in range(n):
                prefix[row + 1][col + 1] = (
                    grid[row][col]
                    + prefix[row][col + 1]
                    + prefix[row + 1][col]
                    - prefix[row][col]
                )

        def region_sum(row: int, col: int, size: int) -> int:
            return (
                prefix[row + size][col + size]
                - prefix[row][col + size]
                - prefix[row + size][col]
                + prefix[row][col]
            )

        def build(row: int, col: int, size: int) -> Node:
            total = region_sum(row, col, size)
            if total == 0 or total == size * size:
                return Node(total > 0, True)
            half = size // 2
            return Node(
                True,
                False,
                build(row, col, half),
                build(row, col + half, half),
                build(row + half, col, half),
                build(row + half, col + half, half),
            )

        return build(0, 0, n)
