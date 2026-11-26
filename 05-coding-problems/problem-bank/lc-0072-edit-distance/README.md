# Edit Distance

## Clean-Room Summary

Given two words, return the minimum number of single-character insertions, deletions, or replacements needed to transform the first word into the second.

## Driver Signature

```java
class Solution {
    public int minDistance(String word1, String word2) {
        // implementation
    }
}
```

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `word1 = "maps", word2 = "maple"` | `2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Full DP table | `O(mn)`. Every pair of prefixes from the two words is evaluated once. | `O(mn)`. The table stores a distance for every prefix pair. |
| 2 | Rolling rows | `O(mn)`. The same prefix-pair transitions are still evaluated. | `O(min(m,n))`. Only one row for the shorter word plus the current row is stored. |

## Pitfalls

- The three operations map to replace, delete, and insert transitions.
- The base row and column represent converting to or from an empty prefix.
- Rolling rows must preserve the previous diagonal value through each column transition.
