from collections import defaultdict
from typing import List


class Solution:
    def groupStrings(self, strings: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for value in strings:
            base = ord(value[0]) - ord('a')
            key = tuple((ord(char) - ord('a') - base) % 26 for char in value)
            groups[key].append(value)
        return list(groups.values())
