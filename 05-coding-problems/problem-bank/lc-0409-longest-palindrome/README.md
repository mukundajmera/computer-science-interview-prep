# Longest Palindrome

## Clean-Room Summary

Compute the maximum palindrome length that can be assembled from the characters of a case-sensitive string.

## Driver Signature

```java
class Solution {
    public int longestPalindrome(String s) {
        // implement
    }
}
```

```python
class Solution:
    def longestPalindrome(self, s: str) -> int:
        # implement
```

## Repo-Authored Cases

- `one odd group can sit in center`
- `all counts even`
- `case-sensitive characters`
- `single repeated character`
- `all unique characters`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Frequency counts | `O(n)`. The string is scanned once and the count table is scanned once. | `O(k)`. The table stores one count per distinct character. |
| 2 | Toggle odd set | `O(n)`. Each character performs constant-time set work. | `O(k)`. The odd set holds at most one entry per distinct character. |

## Pitfalls

- Treat uppercase and lowercase letters as different characters.
- At most one odd-count character can be used as the center.
- Do not need to construct the palindrome itself.
