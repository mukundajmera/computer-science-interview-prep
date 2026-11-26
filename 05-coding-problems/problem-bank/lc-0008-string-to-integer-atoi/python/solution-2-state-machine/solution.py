from __future__ import annotations


class Solution:
    def myAtoi(self, s: str) -> int:
        state = "start"
        sign = 1
        value = 0
        for ch in s:
            if state == "start":
                if ch == " ":
                    continue
                if ch in "+-":
                    sign = -1 if ch == "-" else 1
                    state = "digits"
                    continue
                if not ch.isdigit():
                    return 0
                state = "digits"
            if not ch.isdigit():
                break
            value = value * 10 + ord(ch) - ord("0")
            limit = 2**31 - 1 if sign == 1 else 2**31
            if value > limit:
                return 2**31 - 1 if sign == 1 else -(2**31)
        return sign * value
