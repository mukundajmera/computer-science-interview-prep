from __future__ import annotations

from collections import defaultdict


class WordDictionary:
    def __init__(self) -> None:
        self.by_length: dict[int, list[str]] = defaultdict(list)

    def addWord(self, word: str) -> None:
        self.by_length[len(word)].append(word)

    def search(self, word: str) -> bool:
        for candidate in self.by_length.get(len(word), []):
            if all(pattern == "." or pattern == actual for pattern, actual in zip(word, candidate)):
                return True
        return False
