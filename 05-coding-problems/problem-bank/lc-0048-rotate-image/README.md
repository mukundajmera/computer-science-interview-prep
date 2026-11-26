# Rotate Image

## Clean-Room Summary

Rotate a square matrix clockwise by ninety degrees in place.

## Driver Signature

```java
class Solution {
    public void rotate(int[][] matrix) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        # implementation
```

## Repo-Authored Examples

| matrix | after rotation |
| --- | --- |
| `[[1, 2], [3, 4]]` | `[[3, 1], [4, 2]]` |
| `[[1]]` | `[[1]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Layer four-way swaps | `O(n^2)`. | `O(1)`. |
| 2 | Transpose then reverse rows | `O(n^2)`. | `O(1)`. |

## Pitfalls

- The function returns nothing; the input matrix must be mutated.
- Transpose plus row reversal rotates clockwise, not counterclockwise.
- Layer-by-layer swaps must save one corner before overwriting it.
