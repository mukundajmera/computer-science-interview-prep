# Maximal Square

## Clean-Room Summary

Given a binary character matrix, return the area of the largest square containing only `1` cells.

## Driver Signature

```java
class Solution {
    public int maximalSquare(char[][] matrix) {
        // implementation
    }
}
```

```python
class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[["1","1"],["1","1"]]` | `4` |
| `[["1","1","1"],["1","1","1"],["1","1","1"]]` | `9` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check each candidate square | `O(rows*cols*min(rows, cols)^3)`. Each top-left cell can test many square sizes and each size scans a square. | `O(1)`. Only counters and the best side length are stored. |
| 2 | DP border extension | `O(rows*cols)`. Each cell uses its top, left, and top-left neighbors once. | `O(rows*cols)`. The DP table stores largest square side ending at each cell. |

## Pitfalls

- The return value is area, not side length.
- Character values are `"1"` and `"0"`, not integers.
- A square ending at a cell is limited by the minimum of its three neighboring square sizes.
