# Minimum Number of Arrows to Burst Balloons

## Clean-Room Summary

Given horizontal balloon intervals, find the fewest vertical arrow shots needed so each interval contains at least one shot position.

## Driver Signature

```java
class Solution {
    public int findMinArrowShots(int[][] points) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        # implementation
```

## Repo-Authored Examples

| points | arrows |
| --- | ---: |
| `[[1, 4], [2, 5], [7, 9], [8, 10]]` | `2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort by start and track overlap | `O(n log n)`. | `O(n)`. |
| 2 | Sort by end greedy | `O(n log n)`. | `O(n)`. |

## Pitfalls

- Sort by interval end to place each arrow as late as possible.
- Intervals touching at an endpoint can share one arrow.
- Empty input needs zero arrows.
