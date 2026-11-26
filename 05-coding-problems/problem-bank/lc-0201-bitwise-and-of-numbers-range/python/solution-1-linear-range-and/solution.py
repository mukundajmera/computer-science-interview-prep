class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        result = left
        for value in range(left + 1, right + 1):
            result &= value
            if result == 0:
                return 0
        return result
