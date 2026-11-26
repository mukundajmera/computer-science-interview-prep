# Surrounded Regions

## Clean-Room Summary

Flip every `O` region fully enclosed by `X` cells, while preserving `O` regions connected to the board boundary.

## Driver Signature

```java
class Solution {
    public void solve(char[][] board) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def solve(self, board: List[List[str]]) -> None:
        # implementation
```

## Repo-Authored Examples

| Case | Mutation |
|---|---|
| Interior basin of `O` cells | flipped to `X` |
| Boundary-connected `O` chain | preserved |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Boundary reachability matrix | `O(m*n)`. | `O(m*n)`. |
| 2 | In-place boundary marker | `O(m*n)`. | `O(m*n)` recursion stack. |

## Pitfalls

- Start from boundary `O` cells, not interior cells.
- Do not flip boundary-connected regions.
- Restore temporary markers after flipping enclosed cells.
