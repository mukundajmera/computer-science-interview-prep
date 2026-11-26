from typing import List


class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        rows = len(board)
        cols = len(board[0])
        for row in range(rows):
            for col in range(cols):
                visited = [[False] * cols for _ in range(rows)]
                if self._search(board, word, row, col, 0, visited):
                    return True
        return False

    def _search(self, board: List[List[str]], word: str, row: int, col: int, index: int, visited: List[List[bool]]) -> bool:
        if index == len(word):
            return True
        if row < 0 or row == len(board) or col < 0 or col == len(board[0]):
            return False
        if visited[row][col] or board[row][col] != word[index]:
            return False
        visited[row][col] = True
        found = (
            self._search(board, word, row + 1, col, index + 1, visited)
            or self._search(board, word, row - 1, col, index + 1, visited)
            or self._search(board, word, row, col + 1, index + 1, visited)
            or self._search(board, word, row, col - 1, index + 1, visited)
        )
        visited[row][col] = False
        return found
