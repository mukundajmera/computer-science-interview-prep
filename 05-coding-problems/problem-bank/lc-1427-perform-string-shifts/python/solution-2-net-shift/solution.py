from typing import List


class Solution:
    def stringShift(self, s: str, shift: List[List[int]]) -> str:
        right = sum(amount if direction == 1 else -amount for direction, amount in shift) % len(s)
        return s[-right:] + s[:-right] if right else s
