from typing import List, Set, Tuple


class Solution:
    def palindromePairs(self, words: List[str]) -> List[List[int]]:
        index_by_word = {word: index for index, word in enumerate(words)}
        result: List[List[int]] = []
        seen: Set[Tuple[int, int]] = set()
        for index, word in enumerate(words):
            for split in range(len(word) + 1):
                prefix = word[:split]
                suffix = word[split:]
                if prefix == prefix[::-1]:
                    match = index_by_word.get(suffix[::-1])
                    self._add(result, seen, match, index)
                if split != len(word) and suffix == suffix[::-1]:
                    match = index_by_word.get(prefix[::-1])
                    self._add(result, seen, index, match)
        return result

    def _add(self, result: List[List[int]], seen: Set[Tuple[int, int]], left: int, right: int) -> None:
        if left is None or right is None or left == right:
            return
        pair = (left, right)
        if pair not in seen:
            seen.add(pair)
            result.append([left, right])
