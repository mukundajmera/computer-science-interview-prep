from typing import List


class Solution:
    def hIndex(self, citations: List[int]) -> int:
        h = 0
        citations.sort(reverse=True)
        for count in citations:
            if count >= h + 1:
                h += 1
            else:
                break
        return h
