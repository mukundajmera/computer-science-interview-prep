# Flood Fill

## Clean-Room Summary

Recolor the four-directionally connected component containing the starting cell, but only cells with the original starting color may change.

## Driver Signature

```java
class Solution {
    public int[][] floodFill(int[][] image, int sr, int sc, int color) {
        // implement
    }
}
```

```python
class Solution:
    def floodFill(self, image: List[List[int]], sr: int, sc: int, color: int) -> List[List[int]]:
        # implement
```

## Repo-Authored Cases

- `fills upper-left component`
- `same color is a no-op`
- `fills right-side component`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative DFS | `O(mn)`. Each cell in the connected component is visited at most once, bounded by the whole grid. | `O(mn)`. The explicit stack can contain a path through the entire grid in the worst case. |
| 2 | Iterative BFS | `O(mn)`. Each cell can be enqueued and recolored once. | `O(mn)`. The queue can hold a large frontier in the grid. |

## Pitfalls

- Return early when the replacement color equals the original color.
- Only four-directional neighbors count.
- Mark cells when enqueuing, not after dequeuing, to avoid duplicates.
- Prefer explicit stack or queue traversal in Python for large connected components.
