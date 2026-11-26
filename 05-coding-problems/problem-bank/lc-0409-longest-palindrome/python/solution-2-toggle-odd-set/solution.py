from __future__ import annotations


class Solution:
    def longestPalindrome(self, s: str) -> int:
        odd: set[str] = set()
        length = 0
        for ch in s:
            if ch in odd:
                odd.remove(ch)
                length += 2
            else:
                odd.add(ch)
        return length if not odd else length + 1
