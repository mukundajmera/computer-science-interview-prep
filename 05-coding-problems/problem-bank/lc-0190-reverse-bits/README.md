# Reverse Bits

## Clean-Room Summary

Reverse the order of the 32 bits in the input integer and return the resulting integer value.

## Driver Signature

```java
class Solution {
    public int reverseBits(int n) {
        // implementation
    }
}
```

```python
class Solution:
    def reverseBits(self, n: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `n = 0` | `0` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Bit loop | `O(32)`. The loop has one iteration per bit position. | `O(1)`. Only the input copy, result, and loop index are stored. |
| 2 | Mask swaps | `O(1)`. A fixed number of bit-mask operations is executed. | `O(1)`. Only the transformed integer is stored. |

## Pitfalls

- Use unsigned right shifts in Java when consuming bits.
- Mask Python intermediate values to 32 bits.
- The generated drivers compare Java-compatible signed 32-bit return values.
- The operation always considers exactly 32 bit positions, including leading zeroes.
