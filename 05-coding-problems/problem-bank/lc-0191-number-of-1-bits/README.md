# Number of 1 Bits

## Clean-Room Summary

Given an integer treated as a fixed 32-bit word, return how many bit positions contain a one.

## Driver Signature

```java
class Solution {
    public int hammingWeight(int n) {
        // implementation
    }
}
```

```python
class Solution:
    def hammingWeight(self, n: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `n = 29` | `4` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Fixed bit scan | `O(1)`. Exactly 32 positions are inspected for a fixed-width integer. | `O(1)`. Only the running count and shifted value are stored. |
| 2 | Clear lowest set bit | `O(1)`. At most 32 set bits can be removed from a fixed-width integer. | `O(1)`. The method stores only the count and current word. |

## Pitfalls

- Java must use unsigned right shift when scanning all bit positions.
- Python should mask to 32 bits if negative inputs are ever added later.
- This is constant-time for the LeetCode-style 32-bit contract, even though it loops over bits.
