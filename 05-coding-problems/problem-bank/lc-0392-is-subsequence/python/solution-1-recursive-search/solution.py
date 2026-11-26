class Solution:
    def isSubsequence(self, s: str, t: str) -> bool:
        def search(i: int, j: int) -> bool:
            if i == len(s):
                return True
            if j == len(t):
                return False
            if s[i] == t[j] and search(i + 1, j + 1):
                return True
            return search(i, j + 1)

        return search(0, 0)
