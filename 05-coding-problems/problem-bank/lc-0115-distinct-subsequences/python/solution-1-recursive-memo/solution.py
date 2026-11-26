from functools import lru_cache
class Solution:
    def numDistinct(self, s: str, t: str) -> int:
        @lru_cache(maxsize=None)
        def count(i: int, j: int) -> int:
            if j == len(t):
                return 1
            if i == len(s):
                return 0
            total = count(i + 1, j)
            if s[i] == t[j]:
                total += count(i + 1, j + 1)
            return total
        return count(0, 0)
