from __future__ import annotations


class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        words = tuple(set(wordDict))
        dp = [False] * (len(s) + 1)
        dp[0] = True

        for start in range(len(s)):
            if not dp[start]:
                continue
            for word in words:
                end = start + len(word)
                if s.startswith(word, start):
                    dp[end] = True

        return dp[-1]
