from functools import lru_cache
class Solution:
    def numTrees(self, n: int) -> int:
        @lru_cache(maxsize=None)
        def count(size: int) -> int:
            if size <= 1:
                return 1
            return sum(count(left) * count(size - 1 - left) for left in range(size))
        return count(n)
