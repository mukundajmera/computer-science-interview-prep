# Trapping Rain Water

## Clean-Room Summary

Given bar heights, compute how much water remains after rainfall when each index is bounded by the highest bar on its left and right.

## Driver Signature

```java
class Solution {
    public int trap(int[] height) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def trap(self, height: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| height | water |
| --- | ---: |
| `[3, 0, 2, 0, 4]` | `7` |
| `[2, 1, 2]` | `1` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Prefix and suffix maxima | `O(n)`. | `O(n)`. |
| 2 | Two pointers with running walls | `O(n)`. | `O(1)`. |

## Pitfalls

- Water at an index depends on the smaller side maximum, not the taller side alone.
- Pointer movement is driven by the currently lower boundary.
- Flat or short arrays should naturally contribute zero.
