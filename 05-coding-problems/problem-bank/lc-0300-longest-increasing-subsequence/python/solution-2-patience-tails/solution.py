class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        tails = []
        for value in nums:
            left = 0
            right = len(tails)
            while left < right:
                mid = left + (right - left) // 2
                if tails[mid] < value:
                    left = mid + 1
                else:
                    right = mid
            if left == len(tails):
                tails.append(value)
            else:
                tails[left] = value
        return len(tails)
