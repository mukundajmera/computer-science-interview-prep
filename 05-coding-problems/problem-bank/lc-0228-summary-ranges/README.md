# Summary Ranges

## Clean-Room Summary

Compress a sorted unique integer array into string ranges for consecutive runs.

## Driver Signature

```java
class Solution {
    public List<String> summaryRanges(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def summaryRanges(self, nums: List[int]) -> List[str]:
        # implementation
```

## Repo-Authored Examples

| nums | ranges |
| --- | --- |
| `[-3, -2, -1, 2, 4, 5]` | `["-3->-1", "2", "4->5"]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Run boundary scan | `O(n)`. | `O(1)`. |

## Pitfalls

- Single values are rendered without an arrow.
- A range ends immediately before the next non-consecutive value.
- Empty input returns an empty list.
