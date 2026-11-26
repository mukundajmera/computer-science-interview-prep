from typing import List


class Solution:
    def countBits(self, n: int) -> List[int]:
        answer = [0] * (n + 1)
        for value in range(1, n + 1):
            answer[value] = answer[value >> 1] + (value & 1)
        return answer
