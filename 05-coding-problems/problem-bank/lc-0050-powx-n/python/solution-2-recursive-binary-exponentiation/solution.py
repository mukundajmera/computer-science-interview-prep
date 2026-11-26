from __future__ import annotations


class Solution:
    def myPow(self, x: float, n: int) -> float:
        if n < 0:
            return 1.0 / self._fast_pow(x, -n)
        return self._fast_pow(x, n)

    def _fast_pow(self, base: float, exponent: int) -> float:
        if exponent == 0:
            return 1.0
        half = self._fast_pow(base, exponent // 2)
        squared = half * half
        if exponent & 1:
            return squared * base
        return squared
