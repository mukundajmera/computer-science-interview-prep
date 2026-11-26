# Merge Intervals

## Clean-Room Summary

Given intervals with inclusive starts and ends, combine all overlapping intervals and return the merged ranges sorted by start.

## Driver Signature

```java
class Solution {
    public int[][] merge(int[][] intervals) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Expected |
|---|---|
| `[[5, 7], [1, 3], [2, 4], [9, 11]]` | `[[1, 4], [5, 7], [9, 11]]` |
| `[[3, 5], [5, 8], [10, 12]]` | `[[3, 8], [10, 12]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Repeatedly merge overlapping pairs | `O(n^3)`. | `O(n)`. |
| 2 | Sort by start and merge once | `O(n log n)`. | `O(n)`. |

## Pitfalls

- Sort before the one-pass merge.
- Touching endpoints should merge when intervals are inclusive.
- Copy interval endpoints before mutating output rows.
