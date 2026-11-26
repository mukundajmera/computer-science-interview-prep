# Word Search

## Clean-Room Summary

Given a grid of characters and a word, decide whether the word can be formed by walking through adjacent cells without reusing a cell in the same path.

## Driver Signature

```java
class Solution {
    public boolean exist(char[][] board, String word) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| Board | Word | Expected |
|---|---|---|
| `[[C,O,D],[A,T,E],[R,S,N]]` | `COTS` | `true` |
| `[[A,B],[C,D]]` | `ABA` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS with a separate visited matrix | `O(m*n*4^L)`. | `O(m*n + L)`. |
| 2 | DFS with temporary in-place marking | `O(m*n*4^L)`. | `O(L)`. |

## Pitfalls

- Restore cells or visited flags after every failed path.
- Do not allow a path to reuse the same cell.
- Start DFS only from cells that match the first character.
