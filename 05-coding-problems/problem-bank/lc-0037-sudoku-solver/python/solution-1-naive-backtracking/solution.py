from typing import List


class Solution:
    def solveSudoku(self, board: List[List[str]]) -> None:
        self._solve(board)

    def _solve(self, board: List[List[str]]) -> bool:
        for row in range(9):
            for col in range(9):
                if board[row][col] != ".":
                    continue
                for digit in "123456789":
                    if self._valid(board, row, col, digit):
                        board[row][col] = digit
                        if self._solve(board):
                            return True
                        board[row][col] = "."
                return False
        return True

    def _valid(self, board: List[List[str]], row: int, col: int, digit: str) -> bool:
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for index in range(9):
            if board[row][index] == digit or board[index][col] == digit:
                return False
            if board[box_row + index // 3][box_col + index % 3] == digit:
                return False
        return True
