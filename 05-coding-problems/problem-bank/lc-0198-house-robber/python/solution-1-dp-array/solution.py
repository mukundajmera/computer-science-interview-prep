class Solution:
    def rob(self, nums: List[int]) -> int:
        if not nums:
            return 0
        dp = [0] * (len(nums) + 1)
        dp[1] = nums[0]
        for index in range(2, len(nums) + 1):
            dp[index] = max(dp[index - 1], dp[index - 2] + nums[index - 1])
        return dp[-1]
