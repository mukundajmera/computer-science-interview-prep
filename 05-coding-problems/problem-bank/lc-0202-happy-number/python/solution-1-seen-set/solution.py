class Solution:
    def isHappy(self, n: int) -> bool:
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = self._next(n)
        return n == 1

    def _next(self, value: int) -> int:
        total = 0
        while value > 0:
            value, digit = divmod(value, 10)
            total += digit * digit
        return total
