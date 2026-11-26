from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        write = 0
        current = None
        count = 0
        for num in nums:
            if current is None or num != current:
                current = num
                count = 1
            else:
                count += 1
            if count <= 2:
                nums[write] = num
                write += 1
        return write
