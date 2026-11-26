# Reverse Words in a String

## Clean-Room Summary

Given a string containing words and spaces, return the words in reverse order with single spaces between words and no leading or trailing spaces.

## Driver Signature

```java
class Solution {
    public String reverseWords(String s) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def reverseWords(self, s: str) -> str:
        # implementation
```

## Repo-Authored Examples

| s | Reversed words |
|---|---|
| `  data   structures  matter ` | `matter structures data` |
| `practice` | `practice` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Split, reverse, and join words | `O(n)`. | `O(n)`. |
| 2 | Scan words from right to left | `O(n)`. | `O(n)`. |

## Pitfalls

- The output should normalize internal spacing to a single space.
- Leading and trailing spaces in the input should not appear in the answer.
- Reversing characters is not enough; the unit being reversed is a word.
