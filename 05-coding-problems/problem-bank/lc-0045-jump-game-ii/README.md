# Jump Game II

## Clean-Room Summary

Given maximum jump lengths at each index, return the fewest jumps needed to reach the final index when the input is reachable.

## Driver Signature

```java
class Solution {
    public int jump(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def jump(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| nums | Minimum jumps |
|---|---:|
| `[3, 2, 1, 1, 4]` | `2` |
| `[4, 1, 1, 1, 1, 6]` | `2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Dynamic programming over predecessors | `O(n^2)`. | `O(n)`. |
| 2 | Greedy jump ranges | `O(n)`. | `O(1)`. |

## Pitfalls

- Counting every index visited overestimates the answer; one jump covers a whole reachable range.
- A single-element array needs zero jumps.
- The greedy range boundary should advance only after finishing the current jump range.
