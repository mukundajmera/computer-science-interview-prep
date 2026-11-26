from typing import List


class Solution:
    def areSentencesSimilar(self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool:
        if len(sentence1) != len(sentence2):
            return False
        for left, right in zip(sentence1, sentence2):
            if left == right:
                continue
            if not any((a == left and b == right) or (a == right and b == left) for a, b in similarPairs):
                return False
        return True
