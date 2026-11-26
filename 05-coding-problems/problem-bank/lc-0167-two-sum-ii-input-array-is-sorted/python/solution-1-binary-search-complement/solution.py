from typing import List


class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        for i, value in enumerate(numbers):
            needed = target - value
            lo, hi = i + 1, len(numbers) - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if numbers[mid] == needed:
                    return [i + 1, mid + 1]
                if numbers[mid] < needed:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return []
