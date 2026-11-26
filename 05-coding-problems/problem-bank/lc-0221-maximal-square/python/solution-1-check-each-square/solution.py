from __future__ import annotations


class Solution:
    def maximalSquare(self, matrix: list[list[str]]) -> int:
        rows = len(matrix)
        cols = len(matrix[0])
        best_side = 0

        def is_all_ones(top: int, left: int, side: int) -> bool:
            for row in range(top, top + side):
                for col in range(left, left + side):
                    if matrix[row][col] != "1":
                        return False
            return True

        for row in range(rows):
            for col in range(cols):
                max_side = min(rows - row, cols - col)
                for side in range(1, max_side + 1):
                    if is_all_ones(row, col, side):
                        best_side = max(best_side, side)
                    else:
                        break

        return best_side * best_side
