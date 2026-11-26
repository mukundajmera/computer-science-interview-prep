# Decode Ways

## Clean-Room Summary

Count how many ways a digit string can be partitioned into valid one- or two-digit codes.

## Driver Signature

```java
class Solution {
    public int numDecodings(String s) {
        // implement
    }
}
```

```python
class Solution:
    def numDecodings(self, s: str) -> int:
        # implement
```

## Repo-Authored Cases

- `several paired choices`
- `two valid pair positions`
- `leading zero invalid`
- `trailing impossible zero`
- `zero tied to previous digit`
- `mixed zero and pairs`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Memoized recursion | `O(n)`. Each index is solved once. | `O(n)`. Memoization and recursion depth store up to n entries. |
| 2 | Bottom-up DP | `O(n)`. Each position performs constant work. | `O(n)`. The DP array stores n+1 suffix counts. |
| 3 | Constant-space DP | `O(n)`. Each character position is processed once. | `O(1)`. Only two future counts are retained. |

## Pitfalls

- A standalone zero cannot be decoded.
- Two-digit values are valid only from 10 through 26.
