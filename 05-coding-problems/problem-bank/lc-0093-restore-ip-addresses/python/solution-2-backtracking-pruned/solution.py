from typing import List
class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        result = []
        def backtrack(index: int, parts: List[str]) -> None:
            remaining_parts = 4 - len(parts)
            remaining_digits = len(s) - index
            if remaining_digits < remaining_parts or remaining_digits > remaining_parts * 3:
                return
            if len(parts) == 4:
                if index == len(s):
                    result.append('.'.join(parts))
                return
            for end in range(index + 1, min(len(s), index + 3) + 1):
                part = s[index:end]
                if (len(part) == 1 or part[0] != '0') and int(part) <= 255:
                    parts.append(part)
                    backtrack(end, parts)
                    parts.pop()
        backtrack(0, [])
        return result
