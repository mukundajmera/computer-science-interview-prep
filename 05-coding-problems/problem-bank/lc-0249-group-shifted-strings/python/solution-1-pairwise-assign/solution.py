from typing import List


class Solution:
    def groupStrings(self, strings: List[str]) -> List[List[str]]:
        used = [False] * len(strings)
        groups = []
        for i, first in enumerate(strings):
            if used[i]:
                continue
            group = []
            for j, second in enumerate(strings):
                if not used[j] and self._same(first, second):
                    used[j] = True
                    group.append(second)
            groups.append(group)
        return groups

    def _same(self, a: str, b: str) -> bool:
        if len(a) != len(b):
            return False
        if not a:
            return True
        diff = (ord(b[0]) - ord(a[0])) % 26
        return all((ord(ca) - ord('a') + diff) % 26 == ord(cb) - ord('a') for ca, cb in zip(a, b))
