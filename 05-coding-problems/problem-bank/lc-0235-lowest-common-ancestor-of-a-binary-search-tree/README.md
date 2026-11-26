# Lowest Common Ancestor of a Binary Search Tree

## Clean-Room Summary

In a binary search tree, find the existing node where two target nodes split into different value directions, or where one target is the ancestor of the other.

## Driver Signature

```java
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        // implement
    }
}
```

```python
class Solution:
    def lowestCommonAncestor(self, root: Optional[TreeNode], p: Optional[TreeNode], q: Optional[TreeNode]) -> Optional[TreeNode]:
        # implement
```

## Repo-Authored Cases

- `targets split at root`
- `one target is ancestor`
- `targets split below left child`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Path comparison | `O(h)`. Each target search follows one root-to-leaf path, where h is tree height. | `O(h)`. The two explicit paths can store up to h nodes each. |
| 2 | Iterative BST walk | `O(h)`. The loop moves down one level per iteration. | `O(1)`. Only the current pointer is stored. |

## Pitfalls

- Return the original tree node, not a new node with the same value.
- The first split point is the answer.
- The approach relies on the BST ordering invariant.
- The optimized tier does not need to materialize the paths.
