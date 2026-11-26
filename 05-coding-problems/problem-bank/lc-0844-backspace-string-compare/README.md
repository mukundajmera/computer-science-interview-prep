# Backspace String Compare

## Clean-Room Summary

Compare two typed strings after interpreting each backspace marker as deleting the previous live character when one exists.

## Driver Signature

```java
class Solution {
    public boolean backspaceCompare(String s, String t) {
        // implement
    }
}
```

```python
class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        # implement
```

## Repo-Authored Cases

- `same after one erase`
- `both empty after erases`
- `different final text`
- `leading backspaces ignored`
- `consecutive erases expose mismatch`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Build final strings | `O(n+m)`. Each character from both strings is processed once. | `O(n+m)`. The built strings can store all non-erased characters. |
| 2 | Reverse two pointers | `O(n+m)`. Each character is visited at most once while skipping backspaces. | `O(1)`. Only two pointers and skip counters are stored. |

## Pitfalls

- A backspace at the start or after all characters are deleted has no effect.
- The O(1) approach compares the next live character from the right side of each string.
