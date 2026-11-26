# Average of Levels in Binary Tree

## Clean-Room Summary

For each depth of a binary tree, compute the arithmetic mean of the node values at that depth and return the means from root level to deepest level.

## Driver Signature

```java
class Solution {
    public List<Double> averageOfLevels(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> List[float]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8,4,12,2,6,10,14]` | `[8.0,8.0,8.0]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS level by level | `O(n)`. Every node is visited once. | `O(w)`. The queue stores up to the maximum tree width. |
| 2 | DFS depth buckets | `O(n)`. Every node contributes once to a depth bucket. | `O(h + d)`. Recursion uses height `h`, and sums/counts store `d` levels. |

## Pitfalls

- Divide by the number of nodes on the current level, not by the total number of nodes seen.
- Sparse `null` gaps do not create values; only real nodes contribute to averages.
- Use a wide numeric accumulator before converting to a floating-point average.
