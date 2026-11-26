# Find First and Last Position of Element in Sorted Array

## Clean-Room Summary

Given a sorted array and a target, return the first and last index where the target appears, or [-1, -1] when it is missing.

## Driver Signature

```java
class Solution {
    public int[] searchRange(int[] nums, int target) {
        // implementation
    }
}
```

```python
class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [2, 4, 4, 4, 9, 12]`, `target = 4` | `[1, 3]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear boundary scan | `O(n)`. Every value may be inspected when the target appears late or is absent. | `O(1)`. Only two index variables are maintained. |
| 2 | Lower and upper-bound searches | `O(log n)`. Each boundary search halves the range, and two such searches are run. | `O(1)`. The search uses a constant number of counters. |

## Pitfalls

- A normal binary search can find any occurrence, not necessarily the first or last.
- Use boundary searches: once for the first value not less than target and once for the first value greater than target.
- Empty arrays should return [-1, -1].
