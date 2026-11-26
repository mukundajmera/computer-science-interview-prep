class Solution:
    def hammingWeight(self, n: int) -> int:
        value = n & 0xFFFFFFFF
        count = 0
        for _ in range(32):
            count += value & 1
            value >>= 1
        return count
