class Solution:
    def isValid(self, s: str) -> bool:
        current = s
        previous_length = -1
        while len(current) != previous_length:
            previous_length = len(current)
            current = current.replace("()", "").replace("[]", "").replace("{}", "")
        return current == ""
