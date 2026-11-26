from typing import List


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        for index, expected in enumerate(strs[0]):
            for value in strs[1:]:
                if index == len(value) or value[index] != expected:
                    return strs[0][:index]
        return strs[0]
