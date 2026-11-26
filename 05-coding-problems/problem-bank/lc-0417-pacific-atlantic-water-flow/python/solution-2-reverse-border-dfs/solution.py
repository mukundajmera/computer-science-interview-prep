from typing import List, Set, Tuple


class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        rows = len(heights)
        cols = len(heights[0])

        def fill(starts: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
            seen: Set[Tuple[int, int]] = set()
            stack = starts[:]
            while stack:
                row, col = stack.pop()
                if (row, col) in seen:
                    continue
                seen.add((row, col))
                for row_delta, col_delta in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    next_row = row + row_delta
                    next_col = col + col_delta
                    if (
                        0 <= next_row < rows
                        and 0 <= next_col < cols
                        and heights[next_row][next_col] >= heights[row][col]
                    ):
                        stack.append((next_row, next_col))
            return seen

        pacific = fill([(row, 0) for row in range(rows)] + [(0, col) for col in range(cols)])
        atlantic = fill([(row, cols - 1) for row in range(rows)] + [(rows - 1, col) for col in range(cols)])
        return [[row, col] for row, col in pacific & atlantic]
