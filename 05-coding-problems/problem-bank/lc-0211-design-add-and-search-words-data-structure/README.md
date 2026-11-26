# Design Add and Search Words Data Structure

## Clean-Room Summary

Design a word store that can add words and search query patterns. A dot in a query matches any single character, so query length still matters.

## Driver Signature

```java
class WordDictionary {
    public WordDictionary() {}
    public void addWord(String word) {}
    public boolean search(String word) { return false; }
}
```

```python
class WordDictionary:
    def __init__(self) -> None:
        pass
    def addWord(self, word: str) -> None:
        pass
    def search(self, word: str) -> bool:
        return False
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `WordDictionary(), addWord("stone"), addWord("stove"), search("sto.e"), search("snow")` | `null, null, null, true, false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Bucket words by length and scan candidates | `O(k * L)` per search where `k` is the number of same-length words and `L` is query length. | `O(T)`. All inserted words are stored by length. |
| 2 | Trie with wildcard DFS | `O(26^w * L)` worst case for `w` dots, but `O(L)` when there are no dots. | `O(T)`. The trie stores one node per distinct prefix character path. |

## Pitfalls

- A dot matches exactly one character, not zero or many characters.
- Searching a longer pattern than any stored word should fail even if its prefix matches.
- The trie DFS must branch only on dot positions; normal characters should follow a single edge.
