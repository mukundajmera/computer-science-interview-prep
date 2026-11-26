# Minimum Window Substring

## Clean-Room Summary

Return the shortest substring of one string that contains every required character from another string with multiplicity.

## Driver Signature

```java
class Solution {
    public String minWindow(String s, String t) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        # implementation
```

## Repo-Authored Examples

| s | t | minimum window |
| --- | --- | --- |
| `figehaeci` | `aei` | `aeci` |
| `aabbcc` | `abc` | `abbc` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Expand from every start | `O(n^2)`. | `O(k)`. |
| 2 | Sliding window with formed count | `O(n + m)`. | `O(k)`. |

## Pitfalls

- Required character counts matter when t contains duplicates.
- Shrink the left edge only while the window remains valid.
- Return an empty string when no valid window exists.
- An empty target string returns an empty window.
