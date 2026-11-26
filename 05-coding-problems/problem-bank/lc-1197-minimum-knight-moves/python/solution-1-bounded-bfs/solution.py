from collections import deque


class Solution:
    def minKnightMoves(self, x: int, y: int) -> int:
        moves = ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1))
        limit = max(abs(x), abs(y)) + 6
        queue = deque([(0, 0, 0)])
        seen = {(0, 0)}
        while queue:
            row, col, distance = queue.popleft()
            if row == x and col == y:
                return distance
            for row_delta, col_delta in moves:
                next_row = row + row_delta
                next_col = col + col_delta
                if -limit <= next_row <= limit and -limit <= next_col <= limit and (next_row, next_col) not in seen:
                    seen.add((next_row, next_col))
                    queue.append((next_row, next_col, distance + 1))
        return -1
