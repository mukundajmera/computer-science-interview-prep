# Longest Substring Without Repeating Characters

## Clean-Room Summary

Given a string, return the length of the longest contiguous substring whose characters are all distinct.

## Driver Signature

```java
class Solution {
    public int lengthOfLongestSubstring(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---:|---|
| `"cadence"` | `5` | `"caden"` is the longest duplicate-free prefix. |
| `"moon"` | `2` | Either `"mo"` or `"on"` works. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Start a fresh set at each index | `O(n^2)` because many suffixes may be scanned. | `O(k)` for the current set of unique characters. |
| 2 | Track last seen positions and slide left | `O(n)` because each character is processed once. | `O(k)` for latest positions. |

## Pitfalls

- When a repeated character is left of the current window, do not move the left boundary backward.
- The answer is a length, not the substring itself.
- Empty input should return `0`.
