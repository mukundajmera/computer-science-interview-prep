from typing import List


class Codec:
    def encode(self, strs: List[str]) -> str:
        pieces = []
        for value in strs:
            pieces.append(str(len(value)))
            pieces.append("#")
            pieces.append(value)
        return "".join(pieces)

    def decode(self, s: str) -> List[str]:
        decoded = []
        index = 0
        while index < len(s):
            length = 0
            while s[index] != "#":
                length = length * 10 + int(s[index])
                index += 1
            index += 1
            decoded.append(s[index:index + length])
            index += length
        return decoded
