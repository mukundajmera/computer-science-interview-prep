# Valid Parentheses

## Clean-Room Summary

Given a string made of bracket characters, decide whether every closing bracket matches the nearest unmatched opening bracket of the same type.

## Driver Signature

```java
class Solution {
    public boolean isValid(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def isValid(self, s: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---|---|
| `"{[()]}"` | `true` | Properly nested. |
| `"([)]"` | `false` | Closing order crosses bracket types. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Repeatedly remove adjacent valid pairs | `O(n^2)` because many full scans may be needed. | `O(n)` for replacement strings. |
| 2 | Stack unmatched openers | `O(n)` because each bracket is processed once. | `O(n)` for unmatched openers. |

## Pitfalls

- A closer cannot be accepted if the stack is empty.
- Matching counts alone is not enough; order matters.
- The final stack must be empty.
