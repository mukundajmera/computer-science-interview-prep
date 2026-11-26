from typing import List

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        curr_max = global_max = nums[0]
        for num in nums[1:]:
            curr_max = max(num, curr_max + num)
            global_max = max(global_max, curr_max)
        return global_max

    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        total = 0
        curr_max = curr_min = 0
        global_max = nums[0]
        global_min = nums[0]
        
        for num in nums:
            total += num
            curr_max = max(num, curr_max + num)
            global_max = max(global_max, curr_max)
            curr_min = min(num, curr_min + num)
            global_min = min(global_min, curr_min)
            
        return global_max if global_max < 0 else max(global_max, total - global_min)

    def canJump(self, nums: List[int]) -> bool:
        reachable = 0
        for i, num in enumerate(nums):
            if i > reachable:
                return False
            reachable = max(reachable, i + num)
        return True

    def jump(self, nums: List[int]) -> int:
        jumps = 0
        current_jump_end = 0
        farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == current_jump_end:
                jumps += 1
                current_jump_end = farthest
        return jumps

    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        if sum(gas) < sum(cost):
            return -1
        total = 0
        start = 0
        for i in range(len(gas)):
            total += gas[i] - cost[i]
            if total < 0:
                total = 0
                start = i + 1
        return start

    def candy(self, ratings: List[int]) -> int:
        n = len(ratings)
        candies = [1] * n
        for i in range(1, n):
            if ratings[i] > ratings[i-1]:
                candies[i] = candies[i-1] + 1
        for i in range(n-2, -1, -1):
            if ratings[i] > ratings[i+1]:
                candies[i] = max(candies[i], candies[i+1] + 1)
        return sum(candies)

    def nextPermutation(self, nums: List[int]) -> None:
        n = len(nums)
        i = n - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1
        if i >= 0:
            j = n - 1
            while nums[j] <= nums[i]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        
        left, right = i + 1, n - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
