# N-Queens

## Clean-Room Summary

Return every board arrangement that places n queens so no two share a row, column, or diagonal.

## Driver Signature

```java
class Solution {
    public List<List<String>> solveNQueens(int n) {
        // implement
    }
}
```

```python
class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        # implement
```

## Repo-Authored Cases

- `one queen`
- `two queens impossible`
- `three queens impossible`
- `four queens two boards`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Set backtracking | `O(n!)`. Backtracking tries permutations of columns pruned by diagonal conflicts. | `O(n^2)`. The board plus tracking sets are stored. |
| 2 | Bitmask backtracking | `O(n!)`. The same search tree is explored with lower constant-factor checks. | `O(n^2)`. Result boards dominate output storage; recursion uses O(n). |

## Pitfalls

- The matcher ignores board order, but each board row must be exact.
- Diagonal keys must distinguish row-col and row+col diagonals.
