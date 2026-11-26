# Longest Palindromic Substring

## Clean-Room Summary

Given a string, return a longest contiguous substring that reads the same forward and backward.

## Driver Signature

```java
class Solution {
    public String longestPalindrome(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `"racecarxyz"` | `"racecar"` |
| `"abbaxyzzyx"` | `"xyzzyx"` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check every substring | `O(n^3)`. There are `O(n^2)` substrings and each palindrome check can scan `O(n)` characters. | `O(1)`. Only loop indices are stored besides the returned substring. |
| 2 | Expand from each center | `O(n^2)`. Every center expansion can consume a linear number of characters. | `O(1)`. The algorithm tracks only the best boundaries. |
| 3 | Manacher radius reuse | `O(n)`. Each transformed-string position is expanded only as far as the moving right boundary permits. | `O(n)`. One radius value is stored per transformed position. |

## Pitfalls

- The answer must be a substring, not a subsequence.
- Even-length palindromes need centers between characters.
- Tie handling should be deterministic; these cases avoid ambiguous longest answers.
