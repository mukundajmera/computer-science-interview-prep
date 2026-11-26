from typing import List


class Solution:
    def gameOfLife(self, board: List[List[int]]) -> None:
        snapshot = [row[:] for row in board]
        for row in range(len(board)):
            for col in range(len(board[0])):
                live = self._live_neighbors(snapshot, row, col)
                if snapshot[row][col] == 1:
                    board[row][col] = 1 if live in (2, 3) else 0
                else:
                    board[row][col] = 1 if live == 3 else 0

    def _live_neighbors(self, board: List[List[int]], row: int, col: int) -> int:
        count = 0
        for row_delta in (-1, 0, 1):
            for col_delta in (-1, 0, 1):
                if row_delta == 0 and col_delta == 0:
                    continue
                next_row = row + row_delta
                next_col = col + col_delta
                if 0 <= next_row < len(board) and 0 <= next_col < len(board[0]):
                    count += board[next_row][next_col]
        return count
