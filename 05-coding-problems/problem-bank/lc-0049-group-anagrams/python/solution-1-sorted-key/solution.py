from __future__ import annotations

from collections import defaultdict


class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups = defaultdict(list)
        for word in strs:
            groups["".join(sorted(word))].append(word)
        return [sorted(group) for group in groups.values()]
