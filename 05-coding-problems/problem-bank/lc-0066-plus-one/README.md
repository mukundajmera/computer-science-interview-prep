# Plus One

## Clean-Room Summary

Given an array of decimal digits representing a non-negative integer, add one and return the resulting digit array without leading zeros except for the number zero itself.

## Driver Signature

```java
class Solution {
    public int[] plusOne(int[] digits) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| digits | Result |
|---|---|
| `[4, 2, 9]` | `[4, 3, 0]` |
| `[9, 9, 9]` | `[1, 0, 0, 0]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy then carry | `O(n)`. | `O(n)`. |
| 2 | Mutate from the end | `O(n)`. | `O(1)` auxiliary except overflow output. |

## Pitfalls

- Carry can propagate through every digit when all trailing digits are nine.
- If the first digit overflows, allocate one additional leading digit.
- Do not convert the full number to a primitive integer; it may exceed fixed-width ranges.
