from __future__ import annotations


class Solution:
    def myPow(self, x: float, n: int) -> float:
        exponent = n
        base = x
        if exponent < 0:
            base = 1.0 / base
            exponent = -exponent

        result = 1.0
        while exponent > 0:
            if exponent & 1:
                result *= base
            base *= base
            exponent >>= 1
        return result
