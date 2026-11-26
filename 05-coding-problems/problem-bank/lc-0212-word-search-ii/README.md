# Word Search II

## Clean-Room Summary

Return the dictionary words that can be formed by walking adjacent board cells without reusing a cell in the same word.

## Driver Signature

```java
class Solution {
    public List<String> findWords(char[][] board, String[] words) {
        // implementation
    }
}
```

```python
class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `board = [['a','b','c'], ['d','e','f'], ['g','h','i']], words = ['abe','cfi','zzz']` | `['abe', 'cfi']` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Search each word | `O(wmn4^l)`. For w words, DFS can branch through up to four neighbors across word length l from each board cell. | `O(mn + l)`. The visited matrix tracks board cells and the recursion stack is bounded by the searched word length. |
| 2 | Trie board DFS | `O(mn4^l + totalChars)`. Trie construction uses total word characters, and board DFS explores valid prefix paths instead of every word separately. | `O(totalChars)`. The trie stores the dictionary plus recursion state for board DFS. |

## Pitfalls

- Cells cannot be reused within a single word path.
- Trie pruning avoids restarting a full DFS for every word prefix.
- Remove found words from trie nodes or a result set to avoid duplicates.
