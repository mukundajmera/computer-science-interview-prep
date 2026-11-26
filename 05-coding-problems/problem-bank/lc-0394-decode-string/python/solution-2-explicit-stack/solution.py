from typing import List


class Solution:
    def decodeString(self, s: str) -> str:
        builders: List[List[str]] = []
        counts: List[int] = []
        current: List[str] = []
        repeat = 0
        for char in s:
            if char.isdigit():
                repeat = repeat * 10 + int(char)
            elif char == "[":
                builders.append(current)
                counts.append(repeat)
                current = []
                repeat = 0
            elif char == "]":
                parent = builders.pop()
                parent.append("".join(current) * counts.pop())
                current = parent
            else:
                current.append(char)
        return "".join(current)
