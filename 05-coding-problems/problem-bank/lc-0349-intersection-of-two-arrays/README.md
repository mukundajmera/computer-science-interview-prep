# Intersection of Two Arrays

## Clean-Room Summary

Given two integer arrays, return the unique values that appear in both arrays. The repository drivers use sorted ascending output for deterministic verification.

## Driver Signature

```java
class Solution {
    public int[] intersection(int[] nums1, int[] nums2) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| nums1 | nums2 | Intersection |
|---|---|---|
| `[12, 5, 12, 7, 3]` | `[5, 8, 12, 5, 11]` | `[5, 12]` |
| `[13, 17, 19]` | `[2, 4]` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort unique arrays and two pointers | `O(n log n + m log m)`. | `O(n + m)`. |
| 2 | Hash sets then sorted output | `O(n + m + u log u)`. | `O(n + m)`. |

## Pitfalls

- Return each shared value only once even if it appears repeatedly.
- The original problem allows any order; this repository returns sorted output so generated drivers can use exact equality.
- Use membership of the smaller or second set to avoid duplicate output.
