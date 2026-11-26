# Find the Index of the First Occurrence in a String

## Clean-Room Summary

Given two strings, return the first index where the pattern string begins inside the text string, or `-1` when the pattern never appears.

## Driver Signature

```java
class Solution {
    public int strStr(String haystack, String needle) {
        // implementation
    }
}
```

```python
class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        # implementation
```

## Repo-Authored Examples

| haystack | needle | First index |
|---|---|---:|
| `datastructure` | `struct` | `4` |
| `levelheaded` | `head` | `5` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check every possible start | `O(n * m)`. | `O(1)`. |
| 2 | KMP prefix table | `O(n + m)`. | `O(m)`. |

## Pitfalls

- Stop the direct scan when fewer characters remain than the pattern length.
- An empty pattern is found at index `0`.
- In KMP, the prefix table stores the next viable matched-prefix length after a mismatch.
- Return the beginning of the match, not the index after the match.
