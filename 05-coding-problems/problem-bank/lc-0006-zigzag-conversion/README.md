# Zigzag Conversion

## Clean-Room Summary

Arrange a string across a fixed number of zigzag rows and return the characters read row by row.

## Driver Signature

```java
class Solution {
    public String convert(String s, int numRows) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def convert(self, s: str, numRows: int) -> str:
        # implementation
```

## Repo-Authored Examples

| s | rows | Converted |
|---|---:|---|
| `ABCDEFGHIJK` | `4` | `AGBFHCEIKDJ` |
| `SYSTEM` | `2` | `SSEYTM` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Row simulation with direction flips | `O(n)`. | `O(n)`. |
| 2 | Cycle index walk | `O(n)`. | `O(n)`. |

## Pitfalls

- A single row returns the original string.
- Direction changes happen at the top and bottom row boundaries.
- The direct-index approach alternates vertical and diagonal gaps for middle rows.
