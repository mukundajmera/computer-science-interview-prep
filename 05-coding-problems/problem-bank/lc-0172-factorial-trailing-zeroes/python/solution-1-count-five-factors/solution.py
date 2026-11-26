class Solution:
    def trailingZeroes(self, n: int) -> int:
        zeroes = 0
        for value in range(5, n + 1, 5):
            current = value
            while current % 5 == 0:
                zeroes += 1
                current //= 5
        return zeroes
