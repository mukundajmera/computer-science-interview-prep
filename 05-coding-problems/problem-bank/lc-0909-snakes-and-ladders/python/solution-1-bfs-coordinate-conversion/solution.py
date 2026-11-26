from collections import deque
from typing import List, Tuple


class Solution:
    def snakesAndLadders(self, board: List[List[int]]) -> int:
        n = len(board)

        def coordinates(square: int) -> Tuple[int, int]:
            zero = square - 1
            row_from_bottom = zero // n
            row = n - 1 - row_from_bottom
            col = zero % n
            if row_from_bottom % 2 == 1:
                col = n - 1 - col
            return row, col

        queue = deque([1])
        visited = {1}
        rolls = 0
        while queue:
            for _ in range(len(queue)):
                square = queue.popleft()
                if square == n * n:
                    return rolls
                for die in range(1, 7):
                    if square + die > n * n:
                        break
                    nxt = square + die
                    row, col = coordinates(nxt)
                    if board[row][col] != -1:
                        nxt = board[row][col]
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
            rolls += 1
        return -1
