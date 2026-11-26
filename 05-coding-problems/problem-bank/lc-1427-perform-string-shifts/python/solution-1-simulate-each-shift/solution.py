from typing import List


class Solution:
    def stringShift(self, s: str, shift: List[List[int]]) -> str:
        current = s
        for direction, amount in shift:
            amount %= len(current)
            if direction == 0:
                current = current[amount:] + current[:amount]
            else:
                current = current[-amount:] + current[:-amount] if amount else current
        return current
