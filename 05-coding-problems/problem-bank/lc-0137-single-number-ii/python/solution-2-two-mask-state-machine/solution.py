from typing import List


class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        mask = 0xFFFFFFFF
        ones = 0
        twos = 0
        for value in nums:
            value &= mask
            ones = (ones ^ value) & ~twos & mask
            twos = (twos ^ value) & ~ones & mask
        if ones >= 1 << 31:
            ones -= 1 << 32
        return ones
