# Climbing Stairs

## Clean-Room Summary

Count how many distinct ways there are to reach step `n` when each move can climb either one or two steps.

## Driver Signature

```java
class Solution {
    public int climbStairs(int n) {
        // implementation
    }
}
```

```python
class Solution:
    def climbStairs(self, n: int) -> int:
        # implementation
```

## Repo-Authored Examples

| `n` | Expected | Notes |
|---:|---:|---|
| `4` | `5` | Recurrence combines ways to reach `3` and `2`. |
| `7` | `21` | The count follows a Fibonacci-style progression. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Naive recursive branching | `O(2^n)`. | `O(n)` recursion depth. |
| 2 | Iterative two-state DP | `O(n)`. | `O(1)`. |

## Pitfalls

- The recurrence is `ways(n) = ways(n - 1) + ways(n - 2)`.
- Base cases define `n = 1` as one way and `n = 2` as two ways.
- Avoid exponential recursion for larger inputs.
