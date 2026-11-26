# Longest Valid Parentheses

## Clean-Room Summary

Return the length of the longest contiguous substring that forms a valid parenthesis sequence.

## Driver Signature

```java
class Solution {
    public int longestValidParentheses(String s) {
        // implement
    }
}
```

```python
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        # implement
```

## Repo-Authored Cases

- `single valid pair after prefix`
- `broken middle run`
- `empty string`
- `all opens invalid`
- `nested plus adjacent`
- `unclosed suffix`
- `valid suffix after invalid prefix`
- `nested run between invalid ends`
- `long nested prefix before extra close`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check all substrings | `O(n^3)`. There are O(n^2) substrings and each validation can scan O(n) characters. | `O(1)`. Only counters and loop indexes are stored. |
| 2 | Stack boundaries | `O(n)`. Each character index is pushed and popped at most once. | `O(n)`. The stack can hold all opening indexes in a prefix. |
| 3 | Two-pass counters | `O(n)`. Two linear scans cover the string. | `O(1)`. Only open/close counters and the best length are stored. |

## Pitfalls

- A valid run must be contiguous; do not count separate valid pieces through an invalid boundary.
- A left-to-right counter scan misses excess opening parentheses, so the reverse scan is required.
