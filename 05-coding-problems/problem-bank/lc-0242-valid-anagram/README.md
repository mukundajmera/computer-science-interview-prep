# Valid Anagram

## Clean-Room Summary

Given two strings, decide whether they contain exactly the same characters with exactly the same frequencies.

## Driver Signature

```java
class Solution {
    public boolean isAnagram(String s, String t) {
        // implementation
    }
}
```

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| `s` | `t` | Expected | Notes |
|---|---|---|---|
| `"binary"` | `"brainy"` | `true` | Same six characters. |
| `"mentor"` | `"remote"` | `false` | Same length, but different counts. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort both strings and compare | `O(n log n)` from sorting. | `O(n)` for sorted character storage. |
| 2 | Count character frequencies | `O(n)` because each character is visited once per string. | `O(k)` for distinct characters. |

## Pitfalls

- Check length first; unequal lengths cannot be anagrams.
- Frequency counts matter, not just membership.
- Avoid assuming only lowercase ASCII unless the prompt contract explicitly says so.
