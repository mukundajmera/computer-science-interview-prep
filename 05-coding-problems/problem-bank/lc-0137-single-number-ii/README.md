# Single Number II

## Clean-Room Summary

Given values where every value except one appears three times, return the value that appears once.

## Driver Signature

```java
class Solution {
    public int singleNumber(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [5, 5, -4, 5]` | `-4` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Bit counts modulo three | `O(n)`. There are 32 fixed bit positions, and each position scans all n values. | `O(1)`. Only counters and the reconstructed result are stored. |
| 2 | Two-mask state machine | `O(n)`. Each value updates the two masks once. | `O(1)`. The state is held in two integer masks. |

## Pitfalls

- Modulo counting must reconstruct signed 32-bit answers correctly.
- The two-mask state machine stores bits seen once and twice modulo three.
- Do not use simple XOR; XOR only cancels pairs, not triples.
