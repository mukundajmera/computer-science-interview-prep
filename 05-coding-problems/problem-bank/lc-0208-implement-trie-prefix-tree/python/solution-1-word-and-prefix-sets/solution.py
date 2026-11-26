from __future__ import annotations


class Trie:
    def __init__(self) -> None:
        self.words: set[str] = set()
        self.prefixes: set[str] = set()

    def insert(self, word: str) -> None:
        self.words.add(word)
        for length in range(1, len(word) + 1):
            self.prefixes.add(word[:length])

    def search(self, word: str) -> bool:
        return word in self.words

    def startsWith(self, prefix: str) -> bool:
        return prefix in self.prefixes
