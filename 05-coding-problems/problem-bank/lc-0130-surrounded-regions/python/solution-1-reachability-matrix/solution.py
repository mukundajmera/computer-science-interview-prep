from typing import List


class Solution:
    def solve(self, board: List[List[str]]) -> None:
        rows = len(board)
        cols = len(board[0])
        safe = [[False] * cols for _ in range(rows)]
        for row in range(rows):
            self._mark(board, safe, row, 0)
            self._mark(board, safe, row, cols - 1)
        for col in range(cols):
            self._mark(board, safe, 0, col)
            self._mark(board, safe, rows - 1, col)
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == "O" and not safe[row][col]:
                    board[row][col] = "X"

    def _mark(self, board: List[List[str]], safe: List[List[bool]], row: int, col: int) -> None:
        if row < 0 or row == len(board) or col < 0 or col == len(board[0]):
            return
        if safe[row][col] or board[row][col] != "O":
            return
        safe[row][col] = True
        self._mark(board, safe, row + 1, col)
        self._mark(board, safe, row - 1, col)
        self._mark(board, safe, row, col + 1)
        self._mark(board, safe, row, col - 1)
