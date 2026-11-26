# Binary Tree Upside Down

## Clean-Room Summary

Given the root of a binary tree where all right nodes are either leaf nodes with a sibling or empty, flip it upside down and turn it into a tree where the original right nodes become left nodes and parent nodes become right nodes. Return the new root.

## Driver Signature

```java
class Solution {
    public TreeNode upsideDownBinaryTree(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def upsideDownBinaryTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `root = [1,2,3,4,5]` | `[4,5,2,null,null,3,1]` |
| `root = [1,2,3]` | `[2,3,1]` |
| `root = []` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative pointer reversal | `O(h)`. Iterates along the left spine of height $h$. | `O(1)`. Modifies node pointers in place. |

## Pitfalls

- Save `curr.left` before rewiring pointers because `curr.left` is needed for the next iteration.
- Save `curr.right` in a temporary variable so it can become the left child in the following step.
