class TrieNode:
    def __init__(self):
        self.children = {}
        self.top_k = []


class Trie:
    def __init__(self, k=5):
        self.root = TrieNode()
        self.k = k

    def insert(self, word, frequency):
        node = self.root
        self._update_top_k(node, word, frequency)
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            self._update_top_k(node, word, frequency)

    def _update_top_k(self, node, word, frequency):
        # Update or add
        found = False
        for i, (w, f) in enumerate(node.top_k):
            if w == word:
                node.top_k[i] = (w, frequency)
                found = True
                break

        if not found:
            node.top_k.append((word, frequency))

        # Sort by frequency desc, word asc
        node.top_k.sort(key=lambda x: (-x[1], x[0]))

        # Keep only top k
        if len(node.top_k) > self.k:
            node.top_k.pop()

    def autocomplete(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        return [w for w, f in node.top_k]

    def decay(self, factor=0.9):
        def _decay_node(node):
            new_top_k = []
            for w, f in node.top_k:
                new_f = int(f * factor)
                if new_f > 0:
                    new_top_k.append((w, new_f))
            node.top_k = new_top_k
            for char, child in node.children.items():
                _decay_node(child)
        _decay_node(self.root)
