class Solution:
    def isValid(self, s: str) -> bool:
        matching = {")": "(", "]": "[", "}": "{"}
        stack = []
        for ch in s:
            if ch in matching.values():
                stack.append(ch)
            elif not stack or stack.pop() != matching.get(ch):
                return False
        return not stack
