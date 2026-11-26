from typing import List, Set


class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        for row in range(9):
            if not self._unit_is_valid(board[row][col] for col in range(9)):
                return False
        for col in range(9):
            if not self._unit_is_valid(board[row][col] for row in range(9)):
                return False
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                if not self._unit_is_valid(
                    board[row][col]
                    for row in range(box_row, box_row + 3)
                    for col in range(box_col, box_col + 3)
                ):
                    return False
        return True

    def _unit_is_valid(self, values) -> bool:
        seen: Set[str] = set()
        for value in values:
            if value == ".":
                continue
            if value in seen:
                return False
            seen.add(value)
        return True
