from collections import deque
from typing import Deque, List


class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        candidates: Deque[int] = deque()
        answer: List[int] = []
        for right, value in enumerate(nums):
            while candidates and candidates[0] <= right - k:
                candidates.popleft()
            while candidates and nums[candidates[-1]] <= value:
                candidates.pop()
            candidates.append(right)
            if right >= k - 1:
                answer.append(nums[candidates[0]])
        return answer
