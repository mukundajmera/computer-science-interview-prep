# Substring with Concatenation of All Words

## Clean-Room Summary

Find each starting index where a contiguous block can be split into every required word exactly once.

## Driver Signature

```java
class Solution {
    public List<Integer> findSubstring(String s, String[] words) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| s | words | indices |
| --- | --- | --- |
| `redblublured` | `["red", "blu"]` | `[0, 6]` |
| `aaaaaa` | `["aa", "aa"]` | `[0, 1, 2]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check every possible start | `O(n * m * w)`. | `O(m)`. |
| 2 | Word-length offset sliding window | `O(n * w + r log r)`. | `O(m)`. |

## Pitfalls

- All words have the same length under the platform contract.
- Duplicate words require counts, not set membership.
- Sliding windows should align by word length offsets.
