class Solution:
    def reverse(self, x: int) -> int:
        sign = -1 if x < 0 else 1
        value = int(str(abs(x))[::-1]) * sign
        if value < -2 ** 31 or value > 2 ** 31 - 1:
            return 0
        return value
