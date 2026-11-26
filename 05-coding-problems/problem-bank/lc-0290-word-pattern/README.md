# Word Pattern

## Clean-Room Summary

Check whether pattern characters and words form a one-to-one correspondence.

## Driver Signature

```java
class Solution {
    public boolean wordPattern(String pattern, String s) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| pattern | s | matches |
| --- | --- | --- |
| `abba` | `red blue blue red` | `true` |
| `ab` | `red red` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Two directional maps | `O(n)`. | `O(n)`. |

## Pitfalls

- The number of words must equal the pattern length.
- The mapping must be bijective in both directions.
- Words are tokens separated by single spaces after splitting.
