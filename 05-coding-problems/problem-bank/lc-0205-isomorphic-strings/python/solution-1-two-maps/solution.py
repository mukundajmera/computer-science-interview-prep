class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        forward = {}
        backward = {}
        for left, right in zip(s, t):
            if left in forward and forward[left] != right:
                return False
            if right in backward and backward[right] != left:
                return False
            forward[left] = right
            backward[right] = left
        return True
