from collections import deque


class Solution:
    def minKnightMoves(self, x: int, y: int) -> int:
        x = abs(x)
        y = abs(y)
        moves = ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1))
        queue = deque([(0, 0, 0)])
        seen = {(0, 0)}
        while queue:
            row, col, distance = queue.popleft()
            if row == x and col == y:
                return distance
            for row_delta, col_delta in moves:
                next_row = row + row_delta
                next_col = col + col_delta
                if next_row < -2 or next_col < -2 or next_row > x + 2 or next_col > y + 2:
                    continue
                if (next_row, next_col) not in seen:
                    seen.add((next_row, next_col))
                    queue.append((next_row, next_col, distance + 1))
        return -1
