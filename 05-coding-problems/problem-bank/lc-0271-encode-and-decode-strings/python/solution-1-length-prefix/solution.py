from typing import List


class Codec:
    def encode(self, strs: List[str]) -> str:
        return "".join(f"{len(value)}#{value}" for value in strs)

    def decode(self, s: str) -> List[str]:
        result = []
        index = 0
        while index < len(s):
            marker = s.index("#", index)
            length = int(s[index:marker])
            start = marker + 1
            result.append(s[start:start + length])
            index = start + length
        return result
