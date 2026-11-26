# Insert Interval

## Clean-Room Summary

Given sorted non-overlapping intervals and one new interval, insert the new interval and merge any overlaps.

## Driver Signature

```java
class Solution {
    public int[][] insert(int[][] intervals, int[] newInterval) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Intervals | New interval | Expected |
|---|---|---|
| `[[2, 4], [7, 9]]` | `[5, 6]` | `[[2, 4], [5, 6], [7, 9]]` |
| `[[2, 4], [8, 10]]` | `[3, 9]` | `[[2, 10]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Append, sort, and merge all intervals | `O(n log n)`. | `O(n)`. |
| 2 | Linear three-phase insert | `O(n)`. | `O(n)`. |

## Pitfalls

- Preserve intervals that end before the new interval starts.
- Merge every interval that overlaps the current new interval.
- Append the remaining intervals after the merged new interval.
