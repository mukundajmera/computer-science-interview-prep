# Construct Binary Tree from Inorder and Postorder Traversal

## Clean-Room Summary

Reconstruct the unique binary tree described by inorder and postorder traversal values with distinct node values.

## Driver Signature

```java
class Solution {
    public TreeNode buildTree(int[] inorder, int[] postorder) {
        // implementation
    }
}
```

```python
class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `inorder = [2, 4, 6, 8, 10, 12, 14], postorder = [2, 6, 4, 10, 14, 12, 8]` | `[8, 4, 12, 2, 6, 10, 14]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive slicing | `O(n^2)`. Each recursive step can copy or scan arrays, and skewed trees repeat that work across many levels. | `O(n^2)`. Copied traversal slices can accumulate across recursive calls in skewed inputs. |
| 2 | Index map ranges | `O(n)`. Every node is created once and each inorder lookup is constant time. | `O(n)`. The index map and recursion stack store O(n) state. |

## Pitfalls

- The root position comes from the traversal that visits roots last or first.
- Use an index map for inorder positions to avoid repeated linear scans.
- Return null when the current subtree range is empty.
