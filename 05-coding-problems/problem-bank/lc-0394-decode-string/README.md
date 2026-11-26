# Decode String

## Clean-Room Summary

Expand an encoded string where positive repeat counts apply to bracketed substrings and bracketed groups may be nested.

## Driver Signature

```java
class Solution {
    public String decodeString(String s) {
        // implement
    }
}
```

```python
class Solution:
    def decodeString(self, s: str) -> str:
        # implement
```

## Repo-Authored Cases

- `adjacent groups`
- `nested group`
- `literal suffix`
- `multi digit repeat`
- `literal prefix and suffix`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive descent | `O(n + r)`. The parser reads n encoded characters and appends r decoded characters. | `O(d + r)`. Recursion depth d and output builders store nested work and decoded text. |
| 2 | Explicit stack | `O(n + r)`. Each encoded character is processed once and each decoded character is appended once. | `O(d + r)`. Stacks store nested builders/counts and the decoded output. |

## Pitfalls

- Multi-digit repeat counts must be parsed as one number.
- Plain letters outside brackets are copied directly to the current builder.
