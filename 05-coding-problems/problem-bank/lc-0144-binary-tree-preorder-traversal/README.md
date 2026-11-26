# Binary Tree Preorder Traversal

## Clean-Room Summary

Given the root of a binary tree, return the preorder traversal of its nodes' values.

## Driver Signature

```java
class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def preorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `root = [4,2,6,1,3,5,7]` | `[4,2,1,3,6,5,7]` |
| `root = [3,2,null,1]` | `[3,2,1]` |
| `root = []` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive DFS | `O(n)`. Every node is visited once. | `O(h)`. Call stack proportional to tree height $h$. |
| 2 | Iterative stack | `O(n)`. Every node pushed and popped once. | `O(h)`. Explicit stack holds active path. |

## Pitfalls

- Preorder visits the root first, followed by left subtree, then right subtree.
- In iterative stack traversal, push the right child before the left child so the left child is popped first.
