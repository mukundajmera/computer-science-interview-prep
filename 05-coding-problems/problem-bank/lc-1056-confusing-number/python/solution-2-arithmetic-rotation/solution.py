class Solution:
    def confusingNumber(self, n: int) -> bool:
        original = n
        rotated = 0
        mapping = {0: 0, 1: 1, 6: 9, 8: 8, 9: 6}
        while n > 0:
            digit = n % 10
            if digit not in mapping:
                return False
            rotated = rotated * 10 + mapping[digit]
            n //= 10
        return rotated != original
