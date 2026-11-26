from typing import List
class Solution:
    def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        rows = set()
        for mask in range(1 << len(nums)):
            rows.add(tuple(nums[i] for i in range(len(nums)) if mask & (1 << i)))
        return [list(row) for row in rows]
