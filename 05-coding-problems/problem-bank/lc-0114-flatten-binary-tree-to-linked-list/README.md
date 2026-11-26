# Flatten Binary Tree to Linked List

## Clean-Room Summary

Mutate a binary tree so its nodes follow preorder traversal along `right` pointers only, with every `left` pointer cleared.

## Driver Signature

```java
class Solution {
    public void flatten(TreeNode root) {
        // mutate root
    }
}
```

```python
from typing import Optional


class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        # mutate root
```

## Repo-Authored Examples

Expected mutations are written as TreeNode level-order fixtures. A right-only chain `8 -> 3 -> 1` is represented as `[8,null,3,null,1]`.

| Input root | Mutated root |
|---|---|
| `[8,3,10,1,6,null,14,null,null,4,7]` | `[8,null,3,null,1,null,6,null,4,null,7,null,10,null,14]` |
| `[2,null,5,null,9]` | `[2,null,5,null,9]` |
| `[]` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Preorder buffer and relink | `O(n)`. Collect and relink every node. | `O(n)`. Store all nodes in preorder. |
| 2 | In-place right-spine rewiring | `O(n)`. Each node is rewired into the spine. | `O(1)`. Mutate using pointer references only. |

## Pitfalls

- The method returns nothing; correctness is in the mutated `root`.
- Preserve preorder, not inorder or level order.
- Clear every `left` pointer, including nodes that originally had no right subtree.
