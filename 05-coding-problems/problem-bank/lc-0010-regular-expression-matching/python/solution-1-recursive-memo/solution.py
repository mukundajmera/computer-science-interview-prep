from functools import lru_cache


class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        @lru_cache(maxsize=None)
        def matches(i: int, j: int) -> bool:
            if j == len(p):
                return i == len(s)
            first = i < len(s) and p[j] in {s[i], '.'}
            if j + 1 < len(p) and p[j + 1] == '*':
                return matches(i, j + 2) or (first and matches(i + 1, j))
            return first and matches(i + 1, j + 1)

        return matches(0, 0)
