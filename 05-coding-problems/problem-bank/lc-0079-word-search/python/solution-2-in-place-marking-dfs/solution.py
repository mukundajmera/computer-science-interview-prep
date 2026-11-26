from typing import List


class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        for row in range(len(board)):
            for col in range(len(board[0])):
                if self._search(board, word, row, col, 0):
                    return True
        return False

    def _search(self, board: List[List[str]], word: str, row: int, col: int, index: int) -> bool:
        if index == len(word):
            return True
        if row < 0 or row == len(board) or col < 0 or col == len(board[0]):
            return False
        if board[row][col] != word[index]:
            return False
        original = board[row][col]
        board[row][col] = "#"
        found = (
            self._search(board, word, row + 1, col, index + 1)
            or self._search(board, word, row - 1, col, index + 1)
            or self._search(board, word, row, col + 1, index + 1)
            or self._search(board, word, row, col - 1, index + 1)
        )
        board[row][col] = original
        return found
