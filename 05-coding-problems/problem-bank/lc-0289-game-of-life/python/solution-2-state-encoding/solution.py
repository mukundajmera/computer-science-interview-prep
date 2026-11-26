from typing import List


class Solution:
    def gameOfLife(self, board: List[List[int]]) -> None:
        for row in range(len(board)):
            for col in range(len(board[0])):
                live = self._live_neighbors(board, row, col)
                if board[row][col] == 1 and (live < 2 or live > 3):
                    board[row][col] = -1
                elif board[row][col] == 0 and live == 3:
                    board[row][col] = 2
        for row in range(len(board)):
            for col in range(len(board[0])):
                board[row][col] = 1 if board[row][col] > 0 else 0

    def _live_neighbors(self, board: List[List[int]], row: int, col: int) -> int:
        count = 0
        for row_delta in (-1, 0, 1):
            for col_delta in (-1, 0, 1):
                if row_delta == 0 and col_delta == 0:
                    continue
                next_row = row + row_delta
                next_col = col + col_delta
                if 0 <= next_row < len(board) and 0 <= next_col < len(board[0]):
                    count += 1 if abs(board[next_row][next_col]) == 1 else 0
        return count
