class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _dfs(self, node, prefix, results):
        if len(results) >= 10:
            return
        if node.is_end_of_word:
            results.append(prefix)

        for char in sorted(node.children.keys()):
            self._dfs(node.children[char], prefix + char, results)

    def autocomplete(self, prefix):
        node = self.search_prefix(prefix)
        if not node:
            return []

        results = []
        self._dfs(node, prefix, results)
        return results
