# Letter Combinations of a Phone Number

## Clean-Room Summary

Given digit characters from a phone keypad, return every letter string represented by choosing one mapped letter per digit.

## Driver Signature

```java
class Solution {
    public List<String> letterCombinations(String digits) {
        // implementation
    }
}
```

```python
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `digits = "79"` | `['pw', 'px', 'py', 'pz', 'qw', 'qx', 'qy', 'qz', 'rw', 'rx', 'ry', 'rz', 'sw', 'sx', 'sy', 'sz']` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative expansion | `O(4^n n)`. There can be up to 4^n combinations and each produced string has length n. | `O(4^n n)`. The result list stores every generated string. |
| 2 | Backtracking prefix | `O(4^n n)`. The search emits up to 4^n strings and copies n characters per result. | `O(4^n n)`. The output dominates; the recursion prefix adds O(n) auxiliary stack space. |

## Pitfalls

- The empty input returns an empty result, not a list containing the empty string.
- Digit order determines the character positions inside each generated string.
- Backtracking depth equals the number of digits.
