from typing import List


class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        n = len(matrix)
        for layer in range(n // 2):
            first = layer
            last = n - 1 - layer
            for offset in range(last - first):
                top = matrix[first][first + offset]
                matrix[first][first + offset] = matrix[last - offset][first]
                matrix[last - offset][first] = matrix[last][last - offset]
                matrix[last][last - offset] = matrix[first + offset][last]
                matrix[first + offset][last] = top
