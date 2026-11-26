from __future__ import annotations


class Node:
    def __init__(self) -> None:
        self.children: dict[str, Node] = {}
        self.word = False


class WordDictionary:
    def __init__(self) -> None:
        self.root = Node()

    def addWord(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, Node())
        node.word = True

    def search(self, word: str) -> bool:
        def dfs(index: int, node: Node) -> bool:
            if index == len(word):
                return node.word
            char = word[index]
            if char == ".":
                return any(dfs(index + 1, child) for child in node.children.values())
            child = node.children.get(char)
            return child is not None and dfs(index + 1, child)

        return dfs(0, self.root)
