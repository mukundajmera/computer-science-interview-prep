from typing import List


class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        answer: List[int] = []
        for start in range(len(nums) - k + 1):
            answer.append(max(nums[start:start + k]))
        return answer
