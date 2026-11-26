from typing import List, Set, Tuple


class Solution:
    def areSentencesSimilar(self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool:
        if len(sentence1) != len(sentence2):
            return False
        pairs: Set[Tuple[str, str]] = set()
        for left, right in similarPairs:
            pairs.add((left, right))
            pairs.add((right, left))
        return all(left == right or (left, right) in pairs for left, right in zip(sentence1, sentence2))
