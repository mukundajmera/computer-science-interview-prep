# Longest Common Prefix

## Clean-Room Summary

Given a list of strings, return the longest prefix shared by every string.

## Driver Signature

```java
class Solution {
    public String longestCommonPrefix(String[] strs) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---|---|
| `["system", "synthesis", "syntax"]` | `"sy"` | All strings begin with the same two letters. |
| `["alpha", "beta", "gamma"]` | `""` | No first-character match across all strings. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Shrink a candidate prefix | `O(s)` for total compared characters. | `O(p)` for the candidate prefix. |
| 2 | Scan each character column | `O(s)`. | `O(1)` beyond the returned prefix. |

## Pitfalls

- A single empty string makes the common prefix empty.
- The answer is bounded by the shortest string.
- Stop immediately on the first mismatch.
