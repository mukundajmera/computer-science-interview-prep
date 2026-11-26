# Path Sum III

## Clean-Room Summary

Count downward paths in a binary tree whose values sum to the target; a path may start and end at any nodes as long as it moves downward.

## Driver Signature

```java
class Solution {
    public int pathSum(TreeNode root, int targetSum) {
        // implement
    }
}
```

```python
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        # implement
```

## Repo-Authored Cases

- `multiple downward paths`
- `negative values`
- `single matching node`
- `empty tree`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Start at every node | `O(nh)`. Each node can be included in counts for each ancestor on its path. | `O(h)`. Recursion depth follows tree height. |
| 2 | Prefix-sum counts | `O(n)`. Each node performs constant map work. | `O(h)`. The prefix map contains sums on the current path. |

## Pitfalls

- Paths must go downward but do not need to start at the root.
- Backtrack prefix counts when returning from a subtree.
