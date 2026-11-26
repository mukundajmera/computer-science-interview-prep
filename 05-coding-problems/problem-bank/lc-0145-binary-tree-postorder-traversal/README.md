# Binary Tree Postorder Traversal

## Clean-Room Summary

Given the root of a binary tree, return the postorder traversal of its nodes' values.

## Driver Signature

```java
class Solution {
    public List<Integer> postorderTraversal(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def postorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `root = [4,2,6,1,3,5,7]` | `[1,3,2,5,7,6,4]` |
| `root = [3,2,null,1]` | `[1,2,3]` |
| `root = []` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive DFS | `O(n)`. Every node is visited once. | `O(h)`. Call stack proportional to tree height $h$. |
| 2 | Iterative two stacks | `O(n)`. Every node pushed and popped once. | `O(n)`. Output stack buffers reversed order. |

## Pitfalls

- Postorder visits left subtree first, then right subtree, then root.
- In iterative traversal with two stacks, process root-right-left so that reversing produces left-right-root.
