# Gas Station

## Clean-Room Summary

Given gas gained and travel cost at each station on a cycle, return an index that can complete the full circuit, or `-1` when no such start exists.

## Driver Signature

```java
class Solution {
    public int canCompleteCircuit(int[] gas, int[] cost) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Gas | Cost | Expected | Notes |
|---|---|---:|---|
| `[4, 1, 2]` | `[2, 2, 1]` | `0` | Starting at zero never runs negative. |
| `[2, 0, 0, 3]` | `[1, 1, 1, 1]` | `3` | Earlier starts fail before station `3`. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Simulate each possible start | `O(n^2)`. | `O(1)`. |
| 2 | Greedy reset after a deficit | `O(n)`. | `O(1)`. |

## Pitfalls

- If total gas is less than total cost, no start works.
- Once a candidate start fails at station `i`, every station between the candidate and `i` also fails.
- Return the candidate start only after validating total surplus.
