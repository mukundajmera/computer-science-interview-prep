# Snakes and Ladders

## Clean-Room Summary

On a boustrophedon-numbered board with optional jumps, return the fewest die rolls needed to reach the final square, or -1 when it cannot be reached.

## Driver Signature

```java
class Solution {
    public int snakesAndLadders(int[][] board) {
        // implementation
    }
}
```

```python
class Solution:
    def snakesAndLadders(self, board: List[List[int]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `board = [[-1, -1, -1], [-1, -1, -1], [-1, 9, -1]]` | `1` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS coordinate conversion | `O(n^2)`. At most n^2 squares are visited, with up to six edges checked per square. | `O(n^2)`. The visited set and queue can store all board squares. |
| 2 | Precomputed destinations | `O(n^2)`. Flattening and BFS each touch the board-sized square set. | `O(n^2)`. The destination array, visited array, and queue are board-sized. |

## Pitfalls

- Convert square numbers to board coordinates with alternating row direction.
- Apply at most one jump after a die roll.
- Use BFS levels because each die roll has equal cost.
