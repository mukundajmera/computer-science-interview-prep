# Container With Most Water

## Clean-Room Summary

Given vertical line heights at fixed positions, choose two positions that maximize width times the shorter chosen height.

## Driver Signature

```java
class Solution {
    public int maxArea(int[] height) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def maxArea(self, height: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Heights | Expected | Notes |
|---|---:|---|
| `[4, 3, 2, 1, 4]` | `16` | The two endpoints are best. |
| `[2, 3, 10, 5, 7, 8, 9]` | `36` | The tall inner wall pairs with the far right wall. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Try every pair | `O(n^2)` because all pairs are evaluated. | `O(1)` for counters and best area. |
| 2 | Two pointers, move the shorter side | `O(n)` because each pointer moves inward once per step. | `O(1)`. |

## Pitfalls

- Area is limited by the shorter wall, not the taller one.
- Moving the taller wall while keeping the shorter wall cannot improve height and only shrinks width.
- Inputs with fewer than two lines should produce zero area in this repo's driver cases.
