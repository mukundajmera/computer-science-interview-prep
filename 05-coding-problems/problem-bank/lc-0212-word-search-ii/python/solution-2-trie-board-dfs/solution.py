from typing import Dict, List


class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        trie: Dict[str, dict] = {}
        end = "$"
        for word in words:
            node = trie
            for ch in word:
                node = node.setdefault(ch, {})
            node[end] = word
        rows, cols = len(board), len(board[0])
        result: List[str] = []

        def dfs(row: int, col: int, node: Dict[str, dict]) -> None:
            if row < 0 or row >= rows or col < 0 or col >= cols:
                return
            ch = board[row][col]
            if ch == "#" or ch not in node:
                return
            nxt = node[ch]
            word = nxt.pop(end, None)
            if word is not None:
                result.append(word)
            board[row][col] = "#"
            dfs(row + 1, col, nxt)
            dfs(row - 1, col, nxt)
            dfs(row, col + 1, nxt)
            dfs(row, col - 1, nxt)
            board[row][col] = ch

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, trie)
        return result
