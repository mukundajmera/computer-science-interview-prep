from typing import List


class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        unique = set()
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    if nums[i] + nums[j] + nums[k] == 0:
                        unique.add(tuple(sorted((nums[i], nums[j], nums[k]))))
        return [list(item) for item in sorted(unique)]
