# Unique Paths

## Clean-Room Summary

Count paths from the top-left to bottom-right of an m by n grid when only right and down moves are allowed.

## Driver Signature

```java
class Solution {
    public int uniquePaths(int m, int n) {
        // implement
    }
}
```

```python
class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        # implement
```

## Repo-Authored Cases

- `three by seven`
- `single row`
- `square grid`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Two-dimensional DP | `O(mn)`. Every grid cell is computed once. | `O(mn)`. The full DP grid stores every cell count. |
| 2 | One-dimensional DP | `O(mn)`. The nested loops still visit every logical cell. | `O(n)`. Only one row of n path counts is stored. |

## Pitfalls

- The first row and first column each have exactly one path.
- Use addition from top and left, not diagonal movement.
- The compressed DP row must update left to right.
