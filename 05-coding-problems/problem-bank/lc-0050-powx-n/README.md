# Pow(x, n)

## Clean-Room Summary

Compute a floating-point base raised to an integer exponent. Negative exponents invert the base, and very large exponent magnitudes must be handled without multiplying one step at a time.

## Driver Signature

```java
class Solution {
    public double myPow(double x, int n) {
        // implementation
    }
}
```

```python
class Solution:
    def myPow(self, x: float, n: int) -> float:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `x = 2.5, n = 3` | `15.625` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative binary exponentiation | `O(log |n|)`. Each loop halves the remaining exponent. | `O(1)`. Only the current base, exponent, and answer are stored. |
| 2 | Recursive binary exponentiation | `O(log |n|)`. The recursion halves the exponent at every level. | `O(log |n|)`. The call stack stores one frame per halving. |

## Pitfalls

- Convert the exponent to a wider signed type before negating it; `-2147483648` overflows a 32-bit integer.
- Negative exponents can be handled by inverting the base once and using the positive magnitude.
- Multiplying `|n|` times is too slow for large exponents.
