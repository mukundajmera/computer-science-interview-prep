# Populating Next Right Pointers in Each Node II

## Clean-Room Summary

Given an arbitrary binary tree whose nodes also contain a `next` pointer, connect every node to its immediate neighbor on the same level. The final node on each level must point to `null`.

## Driver Signature

```java
class Solution {
    public Node connect(Node root) {
        // return root after mutating next pointers
    }
}
```

```python
from typing import Optional


class Solution:
    def connect(self, root: Optional[Node]) -> Optional[Node]:
        # return root after mutating next pointers
```

## Repo-Authored Examples

The driver represents input trees as level-order arrays and expected results as the values reached by following `next` pointers on each level.

| Input root | Expected next levels |
|---|---|
| `[10,5,20,3,null,15,30,null,4]` | `[[10],[5,20],[3,15,30],[4]]` |
| `[7]` | `[[7]]` |
| `[]` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Level-order queue linking | `O(n)`. Visit and link every node once. | `O(w)`. Queue stores one level, where `w` is tree width. |
| 2 | Constant-space next-chain traversal | `O(n)`. Consume each established level and append every child once. | `O(1)`. Keep only traversal pointers. |

## Pitfalls

- The tree is not guaranteed to be perfect or complete.
- Always terminate each level by leaving the final node's `next` as `null`.
- The return value should be the same root object after mutation, not a rebuilt tree.
