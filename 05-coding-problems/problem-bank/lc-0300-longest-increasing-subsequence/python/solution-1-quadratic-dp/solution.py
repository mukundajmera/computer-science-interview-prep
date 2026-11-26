class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        dp = [1] * len(nums)
        best = 0
        for index, value in enumerate(nums):
            for previous in range(index):
                if nums[previous] < value:
                    dp[index] = max(dp[index], dp[previous] + 1)
            best = max(best, dp[index])
        return best
