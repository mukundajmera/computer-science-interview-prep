class Solution:
    def reverseBits(self, n: int) -> int:
        result = 0
        value = n & 0xFFFFFFFF
        for _ in range(32):
            result = (result << 1) | (value & 1)
            value >>= 1
        return result if result < 0x80000000 else result - 0x100000000
