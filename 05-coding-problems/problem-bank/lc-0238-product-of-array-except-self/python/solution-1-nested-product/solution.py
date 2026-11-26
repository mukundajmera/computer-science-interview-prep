from typing import List


class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        result = []
        for i in range(len(nums)):
            product = 1
            for j, value in enumerate(nums):
                if i != j:
                    product *= value
            result.append(product)
        return result
