class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        left = len(s) - 1
        right = len(t) - 1
        while left >= 0 or right >= 0:
            left = self._previous_live_index(s, left)
            right = self._previous_live_index(t, right)
            if left < 0 or right < 0:
                return left == right
            if s[left] != t[right]:
                return False
            left -= 1
            right -= 1
        return True

    def _previous_live_index(self, value: str, index: int) -> int:
        skip = 0
        while index >= 0:
            if value[index] == "#":
                skip += 1
            elif skip:
                skip -= 1
            else:
                return index
            index -= 1
        return index
