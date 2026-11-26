class Solution:
    def mySqrt(self, x: int) -> int:
        candidate = 0
        while (candidate + 1) * (candidate + 1) <= x:
            candidate += 1
        return candidate
