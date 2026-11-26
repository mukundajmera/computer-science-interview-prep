class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        def lower_bound(value: int) -> int:
            left = 0
            right = len(nums)
            while left < right:
                mid = left + (right - left) // 2
                if nums[mid] < value:
                    left = mid + 1
                else:
                    right = mid
            return left

        def upper_bound(value: int) -> int:
            left = 0
            right = len(nums)
            while left < right:
                mid = left + (right - left) // 2
                if nums[mid] <= value:
                    left = mid + 1
                else:
                    right = mid
            return left

        first = lower_bound(target)
        if first == len(nums) or nums[first] != target:
            return [-1, -1]
        return [first, upper_bound(target) - 1]
