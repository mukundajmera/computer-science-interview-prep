class Solution:
    def hammingWeight(self, n: int) -> int:
        value = n & 0xFFFFFFFF
        count = 0
        while value:
            value &= value - 1
            count += 1
        return count
