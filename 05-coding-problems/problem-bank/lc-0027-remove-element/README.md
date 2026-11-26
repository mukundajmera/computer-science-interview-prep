# Remove Element

## Clean-Room Summary

Remove every occurrence of a target value by compacting the remaining values into the beginning of the same array and returning the count of kept values.

## Driver Signature

```java
class Solution {
    public int removeElement(int[] nums, int val) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        # implementation
```

## Repo-Authored Examples

| nums | val | Return | Required prefix |
|---|---:|---:|---|
| `[4, 1, 4, 2, 5]` | `4` | `3` | `[1, 2, 5]` |
| `[9, 9, 9]` | `9` | `0` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Build an extra buffer of kept values | `O(n)`. | `O(n)`. |
| 2 | Stable in-place write pointer | `O(n)`. | `O(1)`. |

## Pitfalls

- The returned length determines which prefix positions the driver checks.
- Values beyond the returned length are intentionally ignored.
- This repo's cases expect the kept prefix to preserve input order.
