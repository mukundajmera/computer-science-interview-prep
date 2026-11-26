from typing import List


class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        rows, cols = len(board), len(board[0])

        def exists(word: str) -> bool:
            seen = [[False] * cols for _ in range(rows)]

            def dfs(row: int, col: int, index: int) -> bool:
                if index == len(word):
                    return True
                if row < 0 or row >= rows or col < 0 or col >= cols:
                    return False
                if seen[row][col] or board[row][col] != word[index]:
                    return False
                seen[row][col] = True
                found = (
                    dfs(row + 1, col, index + 1)
                    or dfs(row - 1, col, index + 1)
                    or dfs(row, col + 1, index + 1)
                    or dfs(row, col - 1, index + 1)
                )
                seen[row][col] = False
                return found

            return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))

        return [word for word in words if exists(word)]
