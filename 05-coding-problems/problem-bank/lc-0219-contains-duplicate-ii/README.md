# Contains Duplicate II

## Clean-Room Summary

Given an integer array and distance limit `k`, return whether two equal values appear at indices whose absolute distance is at most `k`.

## Driver Signature

```java
class Solution {
    public boolean containsNearbyDuplicate(int[] nums, int k) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        # implementation
```

## Repo-Authored Examples

| nums | k | Nearby duplicate? |
|---|---:|---|
| `[4, 1, 9, 4]` | `3` | `true` |
| `[4, 1, 9, 4]` | `2` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Compare within each bounded window | `O(n * min(n, k))`. | `O(1)`. |
| 2 | Last seen index map | `O(n)`. | `O(n)`. |

## Pitfalls

- Equal values only count when their index distance is at most `k`.
- A duplicate just outside the window should return false.
- Updating the last seen index is safe because the closest previous duplicate gives the smallest distance for the current index.
