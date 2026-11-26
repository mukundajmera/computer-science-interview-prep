# Longest Increasing Path in a Matrix

## Clean-Room Summary

Find the maximum number of cells in a path that moves orthogonally and strictly increases at every step.

## Driver Signature

```java
class Solution {
    public int longestIncreasingPath(int[][] matrix) {
        // implement
    }
}
```

```python
class Solution:
    def longestIncreasingPath(self, matrix: List[List[int]]) -> int:
        # implement
```

## Repo-Authored Cases

- `turning path through low cell`
- `path bends right then down`
- `single cell`
- `plateau only`
- `single increasing row`
- `single decreasing column can climb upward`
- `snake uses all cells`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Plain DFS | `O(mn * 4^(mn))`. Without caching, branching increasing paths can be re-enumerated from many starts. | `O(mn)`. The recursion depth can include every cell in the longest path. |
| 2 | Memoized DFS | `O(mn)`. Each cell's outgoing edges are evaluated once after memoization. | `O(mn)`. The memo table and recursion stack are bounded by the number of cells. |

## Pitfalls

- Equal-valued neighbors cannot be used because the path must strictly increase.
- Memoization belongs to the starting cell, not to the previous value from a caller.
