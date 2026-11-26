from typing import List


class Solution:
    def solve(self, board: List[List[str]]) -> None:
        rows = len(board)
        cols = len(board[0])
        for row in range(rows):
            self._mark(board, row, 0)
            self._mark(board, row, cols - 1)
        for col in range(cols):
            self._mark(board, 0, col)
            self._mark(board, rows - 1, col)
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == "O":
                    board[row][col] = "X"
                elif board[row][col] == "#":
                    board[row][col] = "O"

    def _mark(self, board: List[List[str]], row: int, col: int) -> None:
        if row < 0 or row == len(board) or col < 0 or col == len(board[0]) or board[row][col] != "O":
            return
        board[row][col] = "#"
        self._mark(board, row + 1, col)
        self._mark(board, row - 1, col)
        self._mark(board, row, col + 1)
        self._mark(board, row, col - 1)
