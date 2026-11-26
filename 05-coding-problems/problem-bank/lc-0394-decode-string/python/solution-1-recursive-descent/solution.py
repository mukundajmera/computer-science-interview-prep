from typing import List


class Solution:
    def decodeString(self, s: str) -> str:
        self._index = 0
        return self._parse(s)

    def _parse(self, s: str) -> str:
        parts: List[str] = []
        while self._index < len(s) and s[self._index] != "]":
            if s[self._index].isdigit():
                repeat = 0
                while self._index < len(s) and s[self._index].isdigit():
                    repeat = repeat * 10 + int(s[self._index])
                    self._index += 1
                self._index += 1
                inner = self._parse(s)
                self._index += 1
                parts.append(inner * repeat)
            else:
                parts.append(s[self._index])
                self._index += 1
        return "".join(parts)
