# Minimum Knight Moves

## Clean-Room Summary

On an unbounded chessboard, return the fewest knight moves needed to reach the target coordinate from the origin.

## Driver Signature

```java
class Solution {
    public int minKnightMoves(int x, int y) {
        // implement
    }
}
```

```python
class Solution:
    def minKnightMoves(self, x: int, y: int) -> int:
        # implement
```

## Repo-Authored Cases

- `already at origin`
- `one knight jump`
- `adjacent axis needs detour`
- `diagonal near origin`
- `two two needs four moves`
- `negative target symmetry`
- `balanced diagonal`
- `larger target`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Bounded BFS | `O(r^2)`. The searched square grows with r = max(|x|, |y|). | `O(r^2)`. The queue and visited set can contain every bounded square. |
| 2 | Symmetric BFS | `O((|x| + 5)(|y| + 5))`. After reflection, BFS stays inside the target rectangle plus a constant negative/positive margin. | `O((|x| + 5)(|y| + 5))`. Visited states stay within the pruned rectangle around the reflected target. |

## Pitfalls

- Near-origin targets such as (1, 0) require temporary moves away from the target.
- Reflecting coordinates is safe because knight moves are symmetric across both axes.
