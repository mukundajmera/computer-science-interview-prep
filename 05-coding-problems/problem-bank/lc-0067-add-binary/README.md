# Add Binary

## Clean-Room Summary

Given two binary strings, return their sum as a binary string without converting the entire value into a fixed-width integer.

## Driver Signature

```java
class Solution {
    public String addBinary(String a, String b) {
        // implementation
    }
}
```

```python
class Solution:
    def addBinary(self, a: str, b: str) -> str:
        # implementation
```

## Repo-Authored Examples

| `a` | `b` | Expected | Notes |
|---|---|---|---|
| `"1001"` | `"111"` | `"10000"` | Carry propagates into a new leading bit. |
| `"10100"` | `"10"` | `"10110"` | No final carry. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Pad shorter input and scan aligned digits | `O(n + m)`. | `O(n + m)` for padded copies plus result. |
| 2 | Scan from the end with two pointers | `O(n + m)`. | `O(n + m)` for only the result buffer. |

## Pitfalls

- Do not rely on fixed-width integer conversion for long inputs.
- Remember to append a remaining carry after both strings are exhausted.
- Build the result in reverse and reverse once at the end.
