# Shortest Path to Get Food

## Clean-Room Summary

Given a grid with one start marker `*`, food markers `#`, blocked cells `X`, and open cells `O`, return the shortest four-direction walk from the start to any food cell.

## Driver Signature

```java
class Solution {
    public int getFood(char[][] grid) {
        // implement
    }
}
```

```python
class Solution:
    def getFood(self, grid: List[List[str]]) -> int:
        # implement
```

## Repo-Authored Cases

- `adjacent food`
- `detour around wall`
- `blocked food`
- `nearest of multiple food cells`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Backtracking search | `O(4^(mn))`. A path can branch to four neighbors until cells are exhausted. | `O(mn)`. The recursion stack and visited grid can cover every cell. |
| 2 | Breadth-first search | `O(mn)`. Each grid cell is enqueued at most once. | `O(mn)`. The queue and visited set can store every open cell. |

## Pitfalls

- BFS is the natural fit because all moves cost one step.
- Blocked cells must never be entered, even if they are on the direct line to food.
