# Construct Quad Tree

## Clean-Room Summary

Build a quad tree from a square binary grid. A region becomes a leaf when every cell in that region has the same value; otherwise it splits into four equal quadrants.

## Driver Signature

```java
class Solution {
    public Node construct(int[][] grid) {
        // return quad tree root
    }
}
```

```python
from typing import List, Optional


class Solution:
    def construct(self, grid: List[List[int]]) -> Optional[Node]:
        # return quad tree root
```

## Repo-Authored Examples

Expected values are nested quad-tree objects with explicit children.

| Input grid | Shape |
|---|---|
| `[[1,0],[0,1]]` | root split into four leaf quadrants |
| `[[0,0],[0,0]]` | one false leaf |
| `[[1,1,0,0],[1,1,0,0],[1,0,0,0],[0,0,0,0]]` | root split, with a nested split in the bottom-left quadrant |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive region scan | `O(n^2 log n)`. Scan all active regions at each depth. | `O(log n)`. Recursion depth, excluding output. |
| 2 | Prefix-sum uniformity checks | `O(n^2)`. Build prefix sums and classify each region in constant time. | `O(n^2)`. Prefix table, excluding output. |

## Pitfalls

- A non-leaf node must have all four children.
- A leaf node should not keep child pointers.
- Internal-node `val` is not semantically important; generated drivers ignore it and compare the split structure plus leaf values.
