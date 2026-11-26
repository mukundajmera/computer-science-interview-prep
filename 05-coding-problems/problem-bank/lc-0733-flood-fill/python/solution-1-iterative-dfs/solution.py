from __future__ import annotations

from typing import List


class Solution:
    def floodFill(self, image: List[List[int]], sr: int, sc: int, color: int) -> List[List[int]]:
        original = image[sr][sc]
        if original == color:
            return image

        stack = [(sr, sc)]
        image[sr][sc] = color
        while stack:
            row, col = stack.pop()
            for next_row, next_col in ((row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)):
                if next_row < 0 or next_row >= len(image) or next_col < 0 or next_col >= len(image[0]):
                    continue
                if image[next_row][next_col] == original:
                    image[next_row][next_col] = color
                    stack.append((next_row, next_col))
        return image
