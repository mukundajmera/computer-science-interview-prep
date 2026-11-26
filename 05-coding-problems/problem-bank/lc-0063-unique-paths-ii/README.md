# Unique Paths II

## Clean-Room Summary

Given a grid where blocked cells cannot be entered, count how many paths move from the top-left cell to the bottom-right cell using only right or down moves.

## Driver Signature

```java
class Solution {
    public int uniquePathsWithObstacles(int[][] obstacleGrid) {
        // implementation
    }
}
```

```python
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]` | `4` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | 2D DP table | `O(mn)`. Every grid cell is evaluated once. | `O(mn)`. A separate table stores one count per cell. |
| 2 | 1D rolling DP | `O(mn)`. Each cell updates one column count once. | `O(n)`. The rolling array stores one path count per column. |

## Pitfalls

- A blocked start or destination means zero paths.
- When a cell is blocked, its path count is zero regardless of top or left neighbors.
- Initialization for the first row and column must stop contributing after an obstacle.
