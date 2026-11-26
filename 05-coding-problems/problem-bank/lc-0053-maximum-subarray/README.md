# Maximum Subarray

## Clean-Room Summary

Return the largest sum obtainable from a non-empty contiguous segment of the input array.

## Driver Signature

```java
class Solution {
    public int maxSubArray(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---:|---|
| `[3, -2, 5, -1]` | `6` | The best segment is `[3, -2, 5]`. |
| `[-4, -2, -7]` | `-2` | A one-element segment can be best. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sum every subarray with a rolling inner sum | `O(n^2)`. | `O(1)`. |
| 2 | Kadane's algorithm | `O(n)`. | `O(1)`. |

## Pitfalls

- Do not allow the empty subarray when all numbers are negative.
- Restart only when the prior running sum hurts the current value.
- Track the global best separately from the current ending sum.
