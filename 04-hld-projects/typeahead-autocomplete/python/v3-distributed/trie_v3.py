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
        found = False
        for i, (w, f) in enumerate(node.top_k):
            if w == word:
                node.top_k[i] = (w, frequency)
                found = True
                break

        if not found:
            node.top_k.append((word, frequency))

        node.top_k.sort(key=lambda x: (-x[1], x[0]))

        if len(node.top_k) > self.k:
            node.top_k.pop()

    def autocomplete(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        return [(w, f) for w, f in node.top_k]


class ShardedTrieManager:
    def __init__(self, num_shards=3, k=5):
        self.num_shards = num_shards
        self.k = k
        self.active_shards = [Trie(k=k) for _ in range(num_shards)]
        self.snapshot_shards = [Trie(k=k) for _ in range(num_shards)]

    def _get_shard_index(self, prefix):
        if not prefix:
            return 0

        char = prefix[0].lower()
        if 'a' <= char <= 'i':
            return 0
        elif 'j' <= char <= 'r':
            return 1
        else:
            return 2

    def insert(self, word, frequency):
        shard_idx = self._get_shard_index(word)
        self.active_shards[shard_idx].insert(word, frequency)

    def autocomplete(self, prefix):
        shard_idx = self._get_shard_index(prefix)
        # Search active shard
        res = self.active_shards[shard_idx].autocomplete(prefix)
        return [w for w, f in res]

    def swap_snapshot(self):
        # Swap active and snapshot for background building
        self.active_shards, self.snapshot_shards = \
            self.snapshot_shards, self.active_shards
        # Clear snapshot shards ready for new build
        self.snapshot_shards = [Trie(k=self.k) for _ in range(self.num_shards)]

    def build_snapshot(self, data):
        # Simulate building a snapshot offline
        for word, freq in data:
            shard_idx = self._get_shard_index(word)
            self.snapshot_shards[shard_idx].insert(word, freq)
