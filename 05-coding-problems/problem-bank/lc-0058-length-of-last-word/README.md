# Length of Last Word

## Clean-Room Summary

Given a string that contains words separated by spaces, return the number of characters in the final word after ignoring trailing spaces.

## Driver Signature

```java
class Solution {
    public int lengthOfLastWord(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        # implementation
```

## Repo-Authored Examples

| s | Length |
|---|---:|
| `alpha beta` | `4` |
| `trail   ` | `5` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Trim and split | `O(n)`. | `O(n)`. |
| 2 | Reverse scan | `O(n)`. | `O(1)`. |

## Pitfalls

- Ignore all trailing spaces before counting.
- Stop counting once the scan crosses the word boundary before the final word.
- A single-word string should return the full string length.
