# Binary Tree Zigzag Level Order Traversal

## Clean-Room Summary

Return the values of a binary tree level by level, reversing the output direction on every other level.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `[[8], [12, 4], [2, 6, 10, 14]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS with alternating inserts | `O(n)`. Each node is dequeued once and each value is inserted into exactly one level list. | `O(n)`. The returned levels store n values; auxiliary queue space is O(w). |
| 2 | DFS depth buckets | `O(n)`. DFS visits each node once and performs O(1) bucket insertion with linked/deque buckets. | `O(n)`. The returned levels store n values; auxiliary recursion stack space is O(h). |

## Pitfalls

- The traversal order of nodes can remain left-to-right; only the values for alternating levels need reversal.
- An empty tree returns an empty list, not a list with an empty level.
- Avoid reversing the final answer globally; the direction alternates per depth.
