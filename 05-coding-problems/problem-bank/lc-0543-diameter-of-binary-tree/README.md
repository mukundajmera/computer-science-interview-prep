# Diameter of Binary Tree

## Clean-Room Summary

Return the maximum number of edges on any path between two nodes in a binary tree.

## Driver Signature

```java
class Solution {
    public int diameterOfBinaryTree(TreeNode root) {
        // implement
    }
}
```

```python
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        # implement
```

## Repo-Authored Cases

- `balanced tree through root`
- `single node`
- `skewed tree`
- `diameter below root`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recompute heights | `O(n^2)`. A skewed tree recomputes heights for many overlapping subtrees. | `O(h)`. Recursion depth follows tree height. |
| 2 | Postorder height | `O(n)`. Every node contributes one height calculation. | `O(h)`. The recursion stack follows tree height. |

## Pitfalls

- Diameter is measured in edges, so a single node has diameter zero.
- The best path may pass through a node below the root.
