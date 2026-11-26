from typing import List


class Solution:
    def countBits(self, n: int) -> List[int]:
        answer = [0] * (n + 1)
        for value in range(n + 1):
            current = value
            count = 0
            while current:
                current &= current - 1
                count += 1
            answer[value] = count
        return answer
