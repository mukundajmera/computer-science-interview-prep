# Minimum Size Subarray Sum

## Clean-Room Summary

Given a positive target and an array of positive integers, return the length of the shortest contiguous subarray whose sum is at least the target. Return `0` when no such subarray exists.

## Driver Signature

```java
class Solution {
    public int minSubArrayLen(int target, int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Target | Nums | Expected | Notes |
|---:|---|---:|---|
| `7` | `[1, 5, 2, 2]` | `2` | Window `[5, 2]` is shortest. |
| `10` | `[1, 2, 3]` | `0` | Total sum is too small. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Extend from each start index | `O(n^2)`. | `O(1)`. |
| 2 | Sliding window over positive values | `O(n)`. | `O(1)`. |

## Pitfalls

- The sliding-window proof depends on positive input values.
- Shrink the left side as long as the current sum still reaches the target.
- Return `0` if no candidate length was found.
