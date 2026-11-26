# Isomorphic Strings

## Clean-Room Summary

Determine whether two strings can be related by a one-to-one character replacement that preserves order.

## Driver Signature

```java
class Solution {
    public boolean isIsomorphic(String s, String t) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| s | t | isomorphic |
| --- | --- | --- |
| `abca` | `zbxz` | `true` |
| `ab` | `aa` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Two directional maps | `O(n)`. | `O(k)`. |
| 2 | Last seen position signatures | `O(n)`. | `O(1)`. |

## Pitfalls

- Both directions of the mapping must be unique.
- A repeated source character must always map to the same target character.
- Different source characters cannot collapse into the same target character.
