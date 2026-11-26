# Product of Array Except Self

## Clean-Room Summary

Return an array where each position contains the product of all input values except the value at that same position.

## Driver Signature

```java
class Solution {
    public int[] productExceptSelf(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---|---|
| `[2, 3, 5]` | `[15, 10, 6]` | Product of the other two values. |
| `[4, 0, 2]` | `[0, 8, 0]` | The zero is excluded only at its own index. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Multiply all other indexes per output | `O(n^2)`. | `O(n)` for the result. |
| 2 | Prefix pass then suffix pass | `O(n)`. | `O(n)` including the result, `O(1)` extra beyond it. |

## Pitfalls

- Division breaks down with zero values and is not needed.
- The neutral product for a single element is `1`.
- Prefix and suffix products must exclude the current element.
