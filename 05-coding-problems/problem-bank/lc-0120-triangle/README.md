# Triangle

## Clean-Room Summary

Given rows of numbers arranged so each row has one more value than the previous row, return the minimum sum along a path from the top to the bottom where each step moves to one of the two adjacent values in the next row.

## Driver Signature

```java
class Solution {
    public int minimumTotal(List<List<Integer>> triangle) {
        // implementation
    }
}
```

```python
class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[[5],[1,6],[4,2,7]]` | `8` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Top-down DP by row and index | `O(n^2)`. Every triangle position is computed once. | `O(n^2)`. A DP table mirrors the triangle. |
| 2 | Bottom-up in-place row buffer | `O(n^2)`. Every value contributes once while scanning upward. | `O(n)`. One row-sized buffer stores the best suffix costs. |

## Pitfalls

- Adjacent in the next row means index `i` or `i + 1`.
- Negative values can make locally larger-looking moves optimal later.
- The number of stored values is quadratic in the number of rows.
