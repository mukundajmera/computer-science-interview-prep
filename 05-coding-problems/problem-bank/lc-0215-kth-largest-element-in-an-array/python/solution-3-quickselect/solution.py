from typing import List


class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        target = len(nums) - k
        left, right = 0, len(nums) - 1
        while left <= right:
            pivot_index = self._partition(nums, left, right)
            if pivot_index == target:
                return nums[pivot_index]
            if pivot_index < target:
                left = pivot_index + 1
            else:
                right = pivot_index - 1
        return nums[target]

    def _partition(self, nums: List[int], left: int, right: int) -> int:
        pivot = nums[right]
        store = left
        for index in range(left, right):
            if nums[index] <= pivot:
                nums[store], nums[index] = nums[index], nums[store]
                store += 1
        nums[store], nums[right] = nums[right], nums[store]
        return store
