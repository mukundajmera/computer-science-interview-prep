from collections import deque
from typing import List


class Solution:
    def snakesAndLadders(self, board: List[List[int]]) -> int:
        n = len(board)
        total = n * n
        destination = [0] * (total + 1)
        for square in range(1, total + 1):
            zero = square - 1
            row_from_bottom = zero // n
            row = n - 1 - row_from_bottom
            col = zero % n
            if row_from_bottom % 2 == 1:
                col = n - 1 - col
            destination[square] = square if board[row][col] == -1 else board[row][col]
        queue = deque([1])
        visited = {1}
        rolls = 0
        while queue:
            for _ in range(len(queue)):
                square = queue.popleft()
                if square == total:
                    return rolls
                for die in range(1, 7):
                    if square + die > total:
                        break
                    nxt = destination[square + die]
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
            rolls += 1
        return -1
