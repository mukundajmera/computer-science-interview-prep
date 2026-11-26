from typing import List, Tuple


class Solution:
    def solveSudoku(self, board: List[List[str]]) -> None:
        rows = [0] * 9
        cols = [0] * 9
        boxes = [0] * 9
        blanks: List[Tuple[int, int]] = []
        for row in range(9):
            for col in range(9):
                if board[row][col] == ".":
                    blanks.append((row, col))
                else:
                    bit = 1 << (ord(board[row][col]) - ord("1"))
                    rows[row] |= bit
                    cols[col] |= bit
                    boxes[(row // 3) * 3 + col // 3] |= bit

        def solve(index: int) -> bool:
            if index == len(blanks):
                return True
            row, col = blanks[index]
            box = (row // 3) * 3 + col // 3
            used = rows[row] | cols[col] | boxes[box]
            for digit in range(9):
                bit = 1 << digit
                if used & bit:
                    continue
                rows[row] |= bit
                cols[col] |= bit
                boxes[box] |= bit
                board[row][col] = str(digit + 1)
                if solve(index + 1):
                    return True
                rows[row] ^= bit
                cols[col] ^= bit
                boxes[box] ^= bit
                board[row][col] = "."
            return False

        solve(0)
