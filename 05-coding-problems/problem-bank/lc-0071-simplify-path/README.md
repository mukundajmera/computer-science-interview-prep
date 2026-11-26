# Simplify Path

## Clean-Room Summary

Normalize an absolute Unix-style path by resolving empty components, current-directory markers, and parent-directory markers.

## Driver Signature

```java
class Solution {
    public String simplifyPath(String path) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def simplifyPath(self, path: str) -> str:
        # implementation
```

## Repo-Authored Examples

| path | simplified |
| --- | --- |
| `/alpha/./beta/../gamma/` | `/alpha/gamma` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Stack path components | `O(n)`. | `O(n)`. |

## Pitfalls

- Multiple slashes do not create meaningful directory names.
- Parent markers at root stay at root.
- The result is always absolute and has no trailing slash unless it is root.
