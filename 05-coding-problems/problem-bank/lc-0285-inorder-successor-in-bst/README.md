# Inorder Successor in BST

## Clean-Room Summary

Return the existing tree node that would appear immediately after `p` in inorder order, or null when `p` is the largest node.

## Driver Signature

```java
class Solution {
    public TreeNode inorderSuccessor(TreeNode root, TreeNode p) {
        // implement
    }
}
```

```python
class Solution:
    def inorderSuccessor(self, root: Optional[TreeNode], p: Optional[TreeNode]) -> Optional[TreeNode]:
        # implement
```

## Repo-Authored Cases

- `right subtree minimum`
- `successor is ancestor`
- `successor inside subtree`
- `maximum has no successor`
- `single node has no successor`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Inorder list | `O(n)`. The traversal can visit every node. | `O(n)`. The inorder list stores every node. |
| 2 | BST walk | `O(h)`. Only one root-to-leaf search path is followed. | `O(1)`. The iterative walk stores a candidate pointer. |

## Pitfalls

- The driver represents `p` and expected nodes as references into `root`.
- The optimized solution depends on BST ordering and unique node values.
