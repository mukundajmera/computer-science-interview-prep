from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if not nums:
            return 0
        unique = [nums[0]]
        for index in range(1, len(nums)):
            if nums[index] != nums[index - 1]:
                unique.append(nums[index])
        nums[:len(unique)] = unique
        return len(unique)
