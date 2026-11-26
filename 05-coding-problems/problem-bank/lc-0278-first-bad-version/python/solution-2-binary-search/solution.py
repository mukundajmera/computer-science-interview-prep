class Solution:
    def firstBadVersion(self, n: int, firstBad: int) -> int:
        left, right = 1, n
        while left < right:
            mid = left + (right - left) // 2
            if self._is_bad_version(mid, firstBad):
                right = mid
            else:
                left = mid + 1
        return left

    def _is_bad_version(self, version: int, first_bad: int) -> bool:
        return version >= first_bad
