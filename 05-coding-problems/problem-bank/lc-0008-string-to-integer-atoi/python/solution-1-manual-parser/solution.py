from __future__ import annotations


class Solution:
    def myAtoi(self, s: str) -> int:
        index = 0
        n = len(s)
        while index < n and s[index] == " ":
            index += 1
        sign = 1
        if index < n and s[index] in "+-":
            sign = -1 if s[index] == "-" else 1
            index += 1
        value = 0
        limit = 2**31 - 1 if sign == 1 else 2**31
        while index < n and s[index].isdigit():
            value = value * 10 + ord(s[index]) - ord("0")
            if value > limit:
                return 2**31 - 1 if sign == 1 else -(2**31)
            index += 1
        return sign * value
