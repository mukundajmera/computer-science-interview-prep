from typing import List


class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        return self._build(s) == self._build(t)

    def _build(self, value: str) -> str:
        stack: List[str] = []
        for char in value:
            if char == "#":
                if stack:
                    stack.pop()
            else:
                stack.append(char)
        return "".join(stack)
