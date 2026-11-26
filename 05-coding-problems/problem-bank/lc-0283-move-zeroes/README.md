# Move Zeroes

## Clean-Room Summary

Move every zero to the end of the array while keeping the non-zero values in their original relative order.

## Driver Signature

```java
class Solution {
    public void moveZeroes(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        # implementation
```

## Repo-Authored Examples

| nums | Mutated nums |
|---|---|
| `[4, 0, 5, 0, 6]` | `[4, 5, 6, 0, 0]` |
| `[0, 0, 2, 3]` | `[2, 3, 0, 0]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Extra buffer of non-zero values | `O(n)`. | `O(n)`. |
| 2 | In-place write pointer then zero fill | `O(n)`. | `O(1)`. |

## Pitfalls

- Preserve the order of non-zero values.
- After moving non-zero values forward, overwrite the remaining suffix with zeroes.
- Arrays without zeroes should remain unchanged.
