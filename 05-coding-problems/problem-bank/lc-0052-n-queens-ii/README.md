# N-Queens II

## Clean-Room Summary

Return how many ways n queens can be placed on an n by n board so that no queen attacks another queen.

## Driver Signature

```java
class Solution {
    public int totalNQueens(int n) {
        // implementation
    }
}
```

```python
class Solution:
    def totalNQueens(self, n: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `n = 5` | `10` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Set backtracking | `O(n!)`. The search branches through permutations of columns, pruned by diagonal conflicts. | `O(n)`. The recursion stack and conflict sets store one row or diagonal entry per placed queen. |
| 2 | Bitmask backtracking | `O(n!)`. The algorithm still explores valid queen placements but prunes conflicts with constant-time bit operations. | `O(n)`. The recursion stack has one frame per row. |

## Pitfalls

- Column, main diagonal, and anti-diagonal conflicts must all be tracked.
- The row number determines how many queens have already been placed.
- Bitmask solutions must mask off only the low n board columns.
