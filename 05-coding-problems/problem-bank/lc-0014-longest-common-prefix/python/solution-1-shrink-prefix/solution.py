from typing import List


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        prefix = strs[0]
        for value in strs[1:]:
            while not value.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix
