# Search a 2D Matrix

## Clean-Room Summary

Given a matrix whose rows are sorted and whose row ranges are globally ordered, decide whether a target value is present.

## Driver Signature

```java
class Solution {
    public boolean searchMatrix(int[][] matrix, int target) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        # implementation
```

## Repo-Authored Examples

| Matrix | Target | Expected |
|---|---:|---|
| `[[2, 4, 8], [12, 16, 20], [25, 30, 40]]` | `16` | `true` |
| `[[2, 4, 8], [12, 16, 20], [25, 30, 40]]` | `15` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Find candidate row, then binary search row | `O(m + log n)`. | `O(1)`. |
| 2 | Binary search flattened coordinates | `O(log(mn))`. | `O(1)`. |

## Pitfalls

- Map a flat index with `row = index / columns` and `column = index % columns`.
- Do not binary search each row independently.
- Handle single-cell matrices.
