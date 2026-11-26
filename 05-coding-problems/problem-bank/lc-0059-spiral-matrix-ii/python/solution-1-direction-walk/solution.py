from typing import List


class Solution:
    def generateMatrix(self, n: int) -> List[List[int]]:
        matrix = [[0] * n for _ in range(n)]
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        row = col = direction = 0
        for value in range(1, n * n + 1):
            matrix[row][col] = value
            next_row = row + directions[direction][0]
            next_col = col + directions[direction][1]
            if not (0 <= next_row < n and 0 <= next_col < n) or matrix[next_row][next_col]:
                direction = (direction + 1) % 4
                next_row = row + directions[direction][0]
                next_col = col + directions[direction][1]
            row, col = next_row, next_col
        return matrix
