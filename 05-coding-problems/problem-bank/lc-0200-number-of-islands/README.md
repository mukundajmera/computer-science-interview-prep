# Number of Islands

## Clean-Room Summary

Count connected groups of land cells in a grid, where land connects horizontally or vertically but not diagonally.

## Driver Signature

```java
class Solution {
    public int numIslands(char[][] grid) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Grid shape | Expected |
|---|---:|
| Three separated four-direction land groups | `3` |
| Diagonal-only land cells | each diagonal cell is separate |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS with a visited matrix | `O(m*n)`. | `O(m*n)`. |
| 2 | In-place DFS that sinks land | `O(m*n)`. | `O(m*n)` recursion stack, no visited matrix. |

## Pitfalls

- Diagonal cells are not connected.
- Mark cells before recursing to avoid revisiting loops.
- In-place sinking mutates the input grid, which is acceptable for these solution tiers.
