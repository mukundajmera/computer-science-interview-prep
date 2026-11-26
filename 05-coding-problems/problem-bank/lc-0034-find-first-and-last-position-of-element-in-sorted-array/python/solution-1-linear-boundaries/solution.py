class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        first = -1
        last = -1
        for index, value in enumerate(nums):
            if value == target:
                if first == -1:
                    first = index
                last = index
        return [first, last]
