# Roman to Integer

## Clean-Room Summary

Convert a Roman numeral string into its integer value by accounting for smaller symbols that appear before larger symbols.

## Driver Signature

```java
class Solution {
    public int romanToInt(String s) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def romanToInt(self, s: str) -> int:
        # implementation
```

## Repo-Authored Examples

| roman | Integer |
|---|---:|
| `XLII` | `42` |
| `CDXLIV` | `444` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Lookahead subtraction scan | `O(n)`. | `O(1)`. |
| 2 | Scan from right with max seen value | `O(n)`. | `O(1)`. |

## Pitfalls

- A symbol is subtracted only when a larger symbol follows it.
- Scanning from the right avoids a separate lookahead for each subtractive pair.
- The input is assumed to be a valid Roman numeral under the problem contract.
