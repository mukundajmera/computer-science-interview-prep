from typing import List


class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
        nums.sort()
        seen = set()
        n = len(nums)
        for a in range(n):
            for b in range(a + 1, n):
                for c in range(b + 1, n):
                    for d in range(c + 1, n):
                        if nums[a] + nums[b] + nums[c] + nums[d] == target:
                            seen.add((nums[a], nums[b], nums[c], nums[d]))
        return [list(row) for row in seen]
