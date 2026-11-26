from typing import List, Set, Tuple


class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        rows = len(heights)
        cols = len(heights[0])
        result: List[List[int]] = []

        def reaches_both(start_row: int, start_col: int) -> bool:
            stack = [(start_row, start_col, heights[start_row][start_col])]
            seen: Set[Tuple[int, int]] = set()
            pacific = False
            atlantic = False
            while stack:
                row, col, previous = stack.pop()
                if row < 0 or col < 0:
                    pacific = True
                    continue
                if row == rows or col == cols:
                    atlantic = True
                    continue
                if (row, col) in seen or heights[row][col] > previous:
                    continue
                seen.add((row, col))
                for row_delta, col_delta in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    stack.append((row + row_delta, col + col_delta, heights[row][col]))
            return pacific and atlantic

        for row in range(rows):
            for col in range(cols):
                if reaches_both(row, col):
                    result.append([row, col])
        return result
