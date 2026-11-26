from typing import Dict, List


class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        prefix_counts: Dict[int, int] = {0: 1}
        prefix = 0
        count = 0
        for value in nums:
            prefix += value
            count += prefix_counts.get(prefix - k, 0)
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        return count
