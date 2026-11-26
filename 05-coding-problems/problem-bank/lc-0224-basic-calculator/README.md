# Basic Calculator

## Clean-Room Summary

Evaluate an arithmetic string containing integers, plus, minus, spaces, and parentheses.

## Driver Signature

```java
class Solution {
    public int calculate(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def calculate(self, s: str) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `7-(2-(3+1))` | `9` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative sign stack | `O(n)`. Each character is read once, and each parenthesis causes O(1) stack work. | `O(d)`. The stack stores two integers per active parenthesis depth d. |
| 2 | Recursive expression parser | `O(n)`. The shared index advances through each character once. | `O(d)`. Recursive calls follow parenthesis nesting depth d. |

## Pitfalls

- Commit the current number before changing signs or closing a parenthesis.
- Parentheses restore both the previous accumulated result and the sign before the group.
- Skip spaces without accidentally ending a multi-digit number.
