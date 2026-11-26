from typing import List


class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        kept = [num for num in nums if num != val]
        nums[:len(kept)] = kept
        return len(kept)
