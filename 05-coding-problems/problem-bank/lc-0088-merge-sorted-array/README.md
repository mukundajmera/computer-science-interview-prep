# Merge Sorted Array

## Clean-Room Summary

Given two sorted integer arrays where the first array has enough trailing capacity, merge the active values from both arrays into the first array in sorted order.

## Driver Signature

```java
class Solution {
    public void merge(int[] nums1, int m, int[] nums2, int n) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        # implementation
```

## Repo-Authored Examples

| nums1 | m | nums2 | n | Mutated nums1 |
|---|---:|---|---:|---|
| `[2, 5, 9, 0, 0, 0]` | `3` | `[1, 6, 10]` | `3` | `[1, 2, 5, 6, 9, 10]` |
| `[-4, 3, 0, 0]` | `2` | `[-5, 7]` | `2` | `[-5, -4, 3, 7]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy into an extra array and sort | `O((m + n) log(m + n))`. | `O(m + n)`. |
| 2 | Reverse three-pointer merge | `O(m + n)`. | `O(1)`. |

## Pitfalls

- Ignore the trailing capacity in `nums1` when reading active values.
- Fill from the end for the optimized approach so unwritten values in `nums1` are not overwritten too early.
- If `nums2` is empty, leave the active prefix unchanged.
