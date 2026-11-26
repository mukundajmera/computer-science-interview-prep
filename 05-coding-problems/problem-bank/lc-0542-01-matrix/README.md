# 01 Matrix

## Clean-Room Summary

For each cell in a binary matrix, compute the distance to the nearest zero using four-directional moves.

## Driver Signature

```java
class Solution {
    public int[][] updateMatrix(int[][] mat) {
        // implement
    }
}
```

```python
class Solution:
    def updateMatrix(self, mat: List[List[int]]) -> List[List[int]]:
        # implement
```

## Repo-Authored Cases

- `single center one`
- `distances grow from corner zeroes`
- `one row matrix`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS from each one | `O((mn)^2)`. Each of mn cells can trigger a BFS over the whole matrix. | `O(mn)`. Each BFS can use a visited matrix and queue over the grid. |
| 2 | Multi-source BFS | `O(mn)`. Every matrix cell is enqueued at most once. | `O(mn)`. The output matrix and queue can cover the full grid. |

## Pitfalls

- Run BFS from all zeros at once for the optimized solution.
- Use four-directional movement only.
- Mark distance when enqueuing to avoid duplicate visits.
