# Spiral Matrix

## Clean-Room Summary

Return matrix values in clockwise spiral order, tightening the top, bottom, left, and right boundaries after each side.

## Driver Signature

```java
class Solution {
    public List<Integer> spiralOrder(int[][] matrix) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| matrix | spiral |
| --- | --- |
| `[[2, 3, 4], [9, 10, 5], [8, 7, 6]]` | `[2, 3, 4, 5, 6, 7, 8, 9, 10]` |
| `[[1], [2], [3]]` | `[1, 2, 3]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Shrinking boundary walk | `O(mn)`. | `O(1)`. |

## Pitfalls

- Check the tightened bounds before walking the bottom row or left column.
- Single-row and single-column matrices should not duplicate values.
- The output size should equal rows times columns.
- Empty matrices return an empty traversal.
