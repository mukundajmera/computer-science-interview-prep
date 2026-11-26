# Jump Game

## Clean-Room Summary

Given jump lengths at each index, decide whether index `0` can reach the final index by repeatedly jumping forward by at most the current length.

## Driver Signature

```java
class Solution {
    public boolean canJump(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def canJump(self, nums: List[int]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---|---|
| `[2, 0, 1, 0]` | `true` | Start can jump over the first zero. |
| `[1, 0, 2]` | `false` | The reachable range stops at index `1`. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Dynamic programming reachability | `O(n^2)`. | `O(n)`. |
| 2 | Greedy farthest reachable index | `O(n)`. | `O(1)`. |

## Pitfalls

- Landing exactly on every intermediate index is not required.
- If the current index is beyond the farthest reach, the scan has failed.
- A single-element array is already at the destination.
