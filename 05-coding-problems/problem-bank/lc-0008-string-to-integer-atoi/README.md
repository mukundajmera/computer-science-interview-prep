# String to Integer (atoi)

## Clean-Room Summary

Parse a signed 32-bit integer from the start of a string after leading spaces, stopping at the first non-digit and clamping overflow.

## Driver Signature

```java
class Solution {
    public int myAtoi(String s) {
        // implement
    }
}
```

```python
class Solution:
    def myAtoi(self, s: str) -> int:
        # implement
```

## Repo-Authored Cases

- `leading spaces and negative sign`
- `positive overflow clamps`
- `negative overflow clamps`
- `sign without digits`
- `stops before letters`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Manual parser with clamping | `O(n)`. At most the leading spaces, sign, and digit prefix are scanned. | `O(1)`. Only index, sign, and accumulated value are stored. |
| 2 | State machine parser | `O(n)`. The parser advances through the string prefix once. | `O(1)`. The machine stores a constant number of state variables. |

## Pitfalls

- Only ordinary leading spaces are skipped.
- A sign must be followed immediately by digits to affect parsing.
- Clamp before accumulated values exceed the signed 32-bit range.
