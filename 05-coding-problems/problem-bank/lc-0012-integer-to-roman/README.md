# Integer to Roman

## Clean-Room Summary

Convert an integer into its Roman numeral representation using the standard decimal-place symbols and subtractive forms.

## Driver Signature

```java
class Solution {
    public String intToRoman(int num) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def intToRoman(self, num: int) -> str:
        # implementation
```

## Repo-Authored Examples

| num | Roman |
|---:|---|
| `42` | `XLII` |
| `444` | `CDXLIV` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Descending symbol table | `O(1)`. | `O(1)`. |
| 2 | Place-value lookup arrays | `O(1)`. | `O(1)`. |

## Pitfalls

- Subtractive forms like IV, IX, XL, XC, CD, and CM should be emitted as whole tokens.
- Descending value tables naturally handle repeated symbols and subtractive forms.
- The input range is bounded by the problem contract, so the output length is constant-bounded in practice.
