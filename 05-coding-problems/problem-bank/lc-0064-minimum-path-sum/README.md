# Minimum Path Sum

## Clean-Room Summary

Given a grid of non-negative costs, return the minimum sum along a path from the top-left cell to the bottom-right cell moving only right or down.

## Driver Signature

```java
class Solution {
    public int minPathSum(int[][] grid) {
        // implementation
    }
}
```

```python
class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[[2, 4, 1], [3, 2, 7], [6, 1, 3]]` | `11` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Separate DP table | `O(mn)`. Each of the m by n cells is computed once. | `O(mn)`. The DP table mirrors the grid size. |
| 2 | In-place grid DP | `O(mn)`. Every cell is updated once. | `O(1)`. No auxiliary table is allocated beyond the input grid storage. |

## Pitfalls

- Each cell depends only on the top and left neighbors after boundary initialization.
- Do not allow diagonal moves.
- Single-row and single-column grids need boundary handling.
