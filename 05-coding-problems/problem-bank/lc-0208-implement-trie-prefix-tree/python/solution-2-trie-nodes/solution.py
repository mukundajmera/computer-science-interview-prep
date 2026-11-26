from __future__ import annotations


class Node:
    def __init__(self) -> None:
        self.children: dict[str, Node] = {}
        self.word = False


class Trie:
    def __init__(self) -> None:
        self.root = Node()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, Node())
        node.word = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.word

    def startsWith(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, text: str) -> Node | None:
        node = self.root
        for char in text:
            node = node.children.get(char)
            if node is None:
                return None
        return node
