class Solution:
    def reverseBits(self, n: int) -> int:
        value = n & 0xFFFFFFFF
        value = ((value & 0xFFFF0000) >> 16) | ((value & 0x0000FFFF) << 16)
        value = ((value & 0xFF00FF00) >> 8) | ((value & 0x00FF00FF) << 8)
        value = ((value & 0xF0F0F0F0) >> 4) | ((value & 0x0F0F0F0F) << 4)
        value = ((value & 0xCCCCCCCC) >> 2) | ((value & 0x33333333) << 2)
        value = ((value & 0xAAAAAAAA) >> 1) | ((value & 0x55555555) << 1)
        value &= 0xFFFFFFFF
        return value if value < 0x80000000 else value - 0x100000000
