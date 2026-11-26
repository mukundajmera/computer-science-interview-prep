# House Robber

## Clean-Room Summary

Given non-negative values along a street, return the maximum value that can be collected without taking from adjacent positions.

## Driver Signature

```java
class Solution {
    public int rob(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def rob(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[4, 1, 2, 9, 1]` | `13` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DP array | `O(n)`. Each house contributes one DP transition. | `O(n)`. The DP array stores one value for each prefix. |
| 2 | Rolling two-state DP | `O(n)`. Each value is processed once. | `O(1)`. The DP state is compressed into two integers. |

## Pitfalls

- The choice at each position depends on the best result two positions back, not just the immediate previous value.
- Keep separate states for taking or skipping the current house.
- One house is a valid input and should return its value.
