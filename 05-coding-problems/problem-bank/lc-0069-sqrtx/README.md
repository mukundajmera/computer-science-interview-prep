# Sqrt(x)

## Clean-Room Summary

Return the greatest integer whose square is less than or equal to the given non-negative integer.

## Driver Signature

```java
class Solution {
    public int mySqrt(int x) {
        // implementation
    }
}
```

```python
class Solution:
    def mySqrt(self, x: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `x = 15` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear square scan | `O(sqrt(x))`. The loop increments once for each possible integer root up to the answer. | `O(1)`. Only the candidate root is stored. |
| 2 | Binary search root | `O(log x)`. Each comparison halves the candidate root range. | `O(1)`. Only boundaries, midpoint, and answer are maintained. |

## Pitfalls

- The return value is floored when x is not a perfect square.
- Use a wider numeric type for mid squared in Java.
- The binary search upper bound can be x / 2 for x greater than one.
