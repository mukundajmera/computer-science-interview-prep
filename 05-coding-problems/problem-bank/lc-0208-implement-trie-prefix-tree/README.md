# Implement Trie (Prefix Tree)

## Clean-Room Summary

Design a prefix tree that can insert words, test whether a full word exists, and test whether any inserted word starts with a given prefix.

## Driver Signature

```java
class Trie {
    public Trie() {}
    public void insert(String word) {}
    public boolean search(String word) { return false; }
    public boolean startsWith(String prefix) { return false; }
}
```

```python
class Trie:
    def __init__(self) -> None:
        pass
    def insert(self, word: str) -> None:
        pass
    def search(self, word: str) -> bool:
        return False
    def startsWith(self, prefix: str) -> bool:
        return False
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `Trie(), insert("orbit"), search("orbit"), search("orb"), startsWith("orb")` | `null, null, true, false, true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Store complete words and every prefix in sets | `O(L)` per insert, search, or prefix check for word length `L`. | `O(T)` where `T` is the total number of stored prefix characters. |
| 2 | Trie nodes with child maps | `O(L)` per operation. Each character advances one edge. | `O(T)`. Nodes represent the distinct prefixes across inserted words. |

## Pitfalls

- A prefix is not automatically a complete word until it is explicitly inserted.
- Shared prefixes should reuse nodes instead of duplicating full strings in the node-based tier.
- `startsWith` can succeed where `search` fails.
