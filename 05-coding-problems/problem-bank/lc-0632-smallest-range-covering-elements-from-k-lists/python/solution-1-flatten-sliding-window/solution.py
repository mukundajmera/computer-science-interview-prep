from collections import defaultdict
from typing import List


class Solution:
    def smallestRange(self, nums: List[List[int]]) -> List[int]:
        values = sorted((value, list_id) for list_id, row in enumerate(nums) for value in row)
        counts = defaultdict(int)
        covered = 0
        left = 0
        best = [values[0][0], values[-1][0]]
        for right, (value, list_id) in enumerate(values):
            counts[list_id] += 1
            if counts[list_id] == 1:
                covered += 1
            while covered == len(nums):
                start = values[left][0]
                end = value
                if end - start < best[1] - best[0] or (end - start == best[1] - best[0] and start < best[0]):
                    best = [start, end]
                left_list = values[left][1]
                counts[left_list] -= 1
                if counts[left_list] == 0:
                    covered -= 1
                left += 1
        return best
