# Contains Duplicate

## Clean-Room Summary

Given an integer array, return whether any value appears at least twice.

## Driver Signature

```java
class Solution {
    public boolean containsDuplicate(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        # implementation
```

## Repo-Authored Examples

| nums | Duplicate? |
|---|---|
| `[4, 1, 9, 4]` | `true` |
| `[11, 2, 8, 4]` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort and scan neighbors | `O(n log n)`. | `O(n)`. |
| 2 | Hash set membership | `O(n)`. | `O(n)`. |

## Pitfalls

- Duplicates can be negative or zero; treat values uniformly.
- Sorting a copy preserves the input array for callers and tests.
- The hash set solution can return as soon as a repeated value is seen.
