class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        left_seen = {}
        right_seen = {}
        for index, (left, right) in enumerate(zip(s, t), start=1):
            if left_seen.get(left, 0) != right_seen.get(right, 0):
                return False
            left_seen[left] = index
            right_seen[right] = index
        return True
