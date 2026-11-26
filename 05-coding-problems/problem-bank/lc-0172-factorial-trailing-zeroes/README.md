# Factorial Trailing Zeroes

## Clean-Room Summary

Return how many zero digits appear at the end of n factorial in decimal form.

## Driver Signature

```java
class Solution {
    public int trailingZeroes(int n) {
        // implementation
    }
}
```

```python
class Solution:
    def trailingZeroes(self, n: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `n = 25` | `6` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count factors in multiples of five | `O(n)`. The total number of factor divisions is bounded by n/5 + n/25 + n/125 + ..., which is linear in n. | `O(1)`. Only the total and current multiple are stored. |
| 2 | Sum powers of five | `O(log n)`. Each step removes a factor of five from n. | `O(1)`. Only the running total and shrinking n are stored. |

## Pitfalls

- Trailing zeroes come from pairs of two and five; fives are the limiting factor.
- Numbers like twenty-five contribute more than one factor of five.
- Computing n factorial directly is unnecessary and quickly overflows.
