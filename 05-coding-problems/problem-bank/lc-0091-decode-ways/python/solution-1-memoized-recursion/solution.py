from functools import lru_cache


class Solution:
    def numDecodings(self, s: str) -> int:
        @lru_cache(maxsize=None)
        def count_from(index: int) -> int:
            if index == len(s):
                return 1
            if s[index] == "0":
                return 0
            total = count_from(index + 1)
            if index + 1 < len(s) and int(s[index:index + 2]) <= 26:
                total += count_from(index + 2)
            return total

        return count_from(0)
