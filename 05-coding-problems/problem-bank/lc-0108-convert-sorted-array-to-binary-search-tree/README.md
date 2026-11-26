# Convert Sorted Array to Binary Search Tree

## Clean-Room Summary

Given a sorted integer array, build a height-balanced binary search tree containing the same values.

## Driver Signature

```java
class Solution {
    public TreeNode sortedArrayToBST(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[2, 5, 9]` | A height-balanced BST whose inorder values are `[2, 5, 9]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive middle split | `O(n)`. Every input value becomes exactly one tree node. | `O(log n)`. The constructed tree is balanced, so recursion depth is logarithmic. |
| 2 | Iterative segment queue | `O(n)`. Each value is turned into one node and each segment is processed once. | `O(n)`. The queue can hold pending child segments across a level. |

## Pitfalls

- The exact shape can vary; the driver accepts any height-balanced BST whose inorder traversal matches the input.
- Return an empty tree for an empty input array.
- Do not insert values one by one into an ordinary BST, because sorted input would create a chain.
