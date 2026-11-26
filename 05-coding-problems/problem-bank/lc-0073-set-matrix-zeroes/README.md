# Set Matrix Zeroes

## Clean-Room Summary

If any matrix cell is zero, set every cell in that row and column to zero in place.

## Driver Signature

```java
class Solution {
    public void setZeroes(int[][] matrix) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        # implementation
```

## Repo-Authored Examples

| matrix | after mutation |
| --- | --- |
| `[[5, 0, 7], [8, 9, 10]]` | `[[0, 0, 0], [8, 0, 10]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Row and column marker sets | `O(mn)`. | `O(m + n)`. |
| 2 | First row and column markers | `O(mn)`. | `O(1)`. |

## Pitfalls

- Mark rows and columns before overwriting values.
- The first row and first column need separate marker flags in the constant-space approach.
- Empty matrices should remain unchanged.
