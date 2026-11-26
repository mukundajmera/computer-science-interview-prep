from typing import List


class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        result = digits[:]
        carry = 1
        index = len(result) - 1
        while index >= 0 and carry:
            value = result[index] + carry
            result[index] = value % 10
            carry = value // 10
            index -= 1
        if carry:
            return [carry] + result
        return result
