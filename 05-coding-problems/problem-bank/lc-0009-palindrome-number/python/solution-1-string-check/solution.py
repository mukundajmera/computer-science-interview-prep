class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0:
            return False
        text = str(x)
        return text == text[::-1]
