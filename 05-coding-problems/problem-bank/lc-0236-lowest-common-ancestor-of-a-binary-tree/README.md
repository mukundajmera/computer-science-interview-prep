# Lowest Common Ancestor of a Binary Tree

## Clean-Room Summary

Given a binary tree root and two existing node references from that tree, return the deepest node that has both targets in its subtree, allowing a target node to be its own ancestor.

## Driver Signature

```java
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        return null;
    }
}
```

```python
from typing import Optional


class Solution:
    def lowestCommonAncestor(
        self,
        root: Optional[TreeNode],
        p: Optional[TreeNode],
        q: Optional[TreeNode],
    ) -> Optional[TreeNode]:
        return None
```

## Repo-Authored Examples

The repository driver represents `p`, `q`, and the expected answer as references into `root`: `{"from": "root", "path": "LR"}` means root, then left, then right.

| root | p | q | Output |
|---|---|---|---|
| `[9,4,13,2,6,11,15,null,3,5,7]` | `LLR` | `LRL` | `L` |
| `[8,4,12,2,6,10,14,1,3]` | `L` | `LLR` | `L` |
| `[5,2,9,2,4,7,9]` | `LL` | `RR` | root |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Parent map and ancestor set | `O(n)`. Build parent links and walk upward from both targets. | `O(n)`. Store parent links and visited ancestors. |
| 2 | Recursive postorder search | `O(n)`. Visit each node at most once. | `O(h)`. Recursion stack follows tree height. |

## Pitfalls

- Compare node identity, not node values; trees can contain duplicate values.
- If one target is an ancestor of the other, that ancestor is the answer.
- Returning a newly allocated node with the same value is incorrect; the answer must be an existing node from the tree.
