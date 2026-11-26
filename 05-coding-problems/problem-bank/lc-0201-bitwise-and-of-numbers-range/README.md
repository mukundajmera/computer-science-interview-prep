# Bitwise AND of Numbers Range

## Clean-Room Summary

Given an inclusive integer range, return the bitwise AND of every value in that range.

## Driver Signature

```java
class Solution {
    public int rangeBitwiseAnd(int left, int right) {
        // implementation
    }
}
```

```python
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `left = 12, right = 15` | `12` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear range AND | `O(right-left+1)`. In the worst case every value in the inclusive range is visited. | `O(1)`. Only the accumulator and loop counter are stored. |
| 2 | Common prefix | `O(log right)`. Each shift removes one binary digit from both endpoints. | `O(1)`. Only the endpoints and shift count are tracked. |

## Pitfalls

- Any bit that changes inside the range becomes zero in the final AND.
- A brute-force scan must avoid integer overflow while moving beyond right.
- The common prefix is the only part that can survive across the entire range.
