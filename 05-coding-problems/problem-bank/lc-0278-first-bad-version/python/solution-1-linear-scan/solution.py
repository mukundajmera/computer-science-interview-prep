class Solution:
    def firstBadVersion(self, n: int, firstBad: int) -> int:
        for version in range(1, n + 1):
            if self._is_bad_version(version, firstBad):
                return version
        return n

    def _is_bad_version(self, version: int, first_bad: int) -> bool:
        return version >= first_bad
