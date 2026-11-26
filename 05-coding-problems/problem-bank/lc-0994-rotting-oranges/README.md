# Rotting Oranges

## Clean-Room Summary

Each minute, rotten oranges infect adjacent fresh oranges; return the minutes required to rot every fresh orange, or -1 if some fresh orange is unreachable.

## Driver Signature

```java
class Solution {
    public int orangesRotting(int[][] grid) {
        // implement
    }
}
```

```python
class Solution:
    def orangesRotting(self, grid: List[List[int]]) -> int:
        # implement
```

## Repo-Authored Cases

- `two rotten sources meet in middle`
- `no fresh oranges`
- `isolated fresh oranges remain`
- `fresh orange without source`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Minute-by-minute simulation | `O((mn)^2)`. Each minute can scan the whole grid, and there can be O(mn) minutes. | `O(mn)`. The next-wave list can hold many cells. |
| 2 | Multi-source BFS | `O(mn)`. Every grid cell is enqueued at most once. | `O(mn)`. The queue can contain a full layer of grid cells. |

## Pitfalls

- Use multi-source BFS so all initial rotten oranges spread at minute zero.
- Increment minutes once per BFS layer, not once per cell.
- Return `-1` when fresh oranges remain after the queue is exhausted.
