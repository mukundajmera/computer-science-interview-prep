from typing import List
class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        result = []
        for a in range(1, 4):
            for b in range(1, 4):
                for c in range(1, 4):
                    for d in range(1, 4):
                        if a + b + c + d == len(s):
                            parts = [s[:a], s[a:a+b], s[a+b:a+b+c], s[a+b+c:]]
                            if all(self._valid(part) for part in parts):
                                result.append('.'.join(parts))
        return result
    def _valid(self, part: str) -> bool:
        return not (len(part) > 1 and part[0] == '0') and int(part) <= 255
