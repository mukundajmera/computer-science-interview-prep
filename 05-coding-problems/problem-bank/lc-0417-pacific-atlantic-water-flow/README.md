# Pacific Atlantic Water Flow

## Clean-Room Summary

Return coordinates whose height can flow through non-increasing moves to both the top/left border set and the bottom/right border set.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> pacificAtlantic(int[][] heights) {
        // implement
    }
}
```

```python
class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        # implement
```

## Repo-Authored Cases

- `ridge reaches both borders`
- `single cell`
- `one row`
- `flat plateau`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Search from each cell | `O((mn)^2)`. Each cell can explore much of the grid. | `O(mn)`. A visited set is needed per search. |
| 2 | Reverse border DFS | `O(mn)`. Each ocean traversal visits each cell at most once. | `O(mn)`. Two reachability matrices and traversal stack are stored. |

## Pitfalls

- Reverse the flow direction from borders to avoid launching a search from every cell.
- A move in reverse traversal is allowed only into equal or higher height.
