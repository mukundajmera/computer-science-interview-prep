from typing import List


class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        prefix = [0]
        for value in nums:
            prefix.append(prefix[-1] + (1 if value == 1 else -1))
        best = 0
        for start in range(len(prefix)):
            for end in range(start + 1, len(prefix)):
                if prefix[start] == prefix[end]:
                    best = max(best, end - start)
        return best
