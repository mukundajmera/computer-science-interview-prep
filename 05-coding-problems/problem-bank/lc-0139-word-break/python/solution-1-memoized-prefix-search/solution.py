from __future__ import annotations


class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        words = tuple(set(wordDict))
        memo: dict[int, bool] = {}

        def can_break(start: int) -> bool:
            if start == len(s):
                return True
            if start in memo:
                return memo[start]
            for word in words:
                end = start + len(word)
                if s.startswith(word, start) and can_break(end):
                    memo[start] = True
                    return True
            memo[start] = False
            return False

        return can_break(0)
