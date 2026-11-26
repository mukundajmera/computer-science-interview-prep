from typing import List


class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        result = 0
        for bit in range(32):
            count = 0
            for value in nums:
                if ((value & 0xFFFFFFFF) >> bit) & 1:
                    count += 1
            if count % 3:
                result |= 1 << bit
        if result >= 1 << 31:
            result -= 1 << 32
        return result
