class Solution:
    def findMin(self, nums: List[int]) -> int:
        best = nums[0]
        for value in nums:
            best = min(best, value)
        return best
