# Game of Life

## Clean-Room Summary

Update a binary grid by applying the next-state rules to every cell at the same time.

## Driver Signature

```java
class Solution {
    public void gameOfLife(int[][] board) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def gameOfLife(self, board: List[List[int]]) -> None:
        # implementation
```

## Repo-Authored Examples

| Board | Next state |
|---|---|
| vertical three-cell line | horizontal three-cell line |
| 2x2 live block | unchanged |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy original board and update input | `O(m*n)`. | `O(m*n)`. |
| 2 | Encode transitions in place | `O(m*n)`. | `O(1)`. |

## Pitfalls

- All cells must use the original generation when counting neighbors.
- Transitional values must preserve enough information to decode original live/dead state.
- Apply a final normalization pass after in-place encoding.
