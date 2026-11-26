# Maximum Depth of Binary Tree

## Clean-Room Summary

Given a binary tree, return the number of nodes on the longest root-to-leaf path.

## Driver Signature

```java
class Solution {
    public int maxDepth(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, null, 14, 1]` | `4` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive DFS depth | `O(n)`. | `O(h)`. |
| 2 | Iterative BFS levels | `O(n)`. | `O(w)`. |

## Pitfalls

- An empty tree has depth zero.
- Count nodes on the path, not edges.
- A skewed tree can make recursive stack depth linear.
