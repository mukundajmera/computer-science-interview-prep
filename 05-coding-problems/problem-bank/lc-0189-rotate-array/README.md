# Rotate Array

## Clean-Room Summary

Given an integer array and a non-negative shift count, rotate the array in place so each element moves right by `k` positions modulo the array length.

## Driver Signature

```java
class Solution {
    public void rotate(int[] nums, int k) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        # implementation
```

## Repo-Authored Examples

| nums | k | Mutated nums |
|---|---:|---|
| `[10, 20, 30, 40, 50]` | `2` | `[40, 50, 10, 20, 30]` |
| `[1, 2, 3, 4]` | `4` | `[1, 2, 3, 4]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Extra rotated copy | `O(n)`. | `O(n)`. |
| 2 | Reverse three sections | `O(n)`. | `O(1)`. |

## Pitfalls

- Reduce `k` modulo the array length before rotating.
- The method returns nothing; the driver verifies the mutated array.
- This repository treats an empty array as a no-op for defensive driver coverage.
- For the reversal approach, reverse the whole array, then the first `k`, then the remaining suffix.
