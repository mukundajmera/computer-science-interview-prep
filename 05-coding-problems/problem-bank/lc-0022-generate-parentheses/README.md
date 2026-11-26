# Generate Parentheses

## Clean-Room Summary

Return every balanced parenthesis string that can be formed with n opening and n closing parentheses.

## Driver Signature

```java
class Solution {
    public List<String> generateParenthesis(int n) {
        // implementation
    }
}
```

```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `n = 2` | `['(())', '()()']` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Backtracking counts | `O(C_n n)`. There are C_n valid strings and each output string has length 2n. | `O(C_n n)`. The result stores every string; the recursion path uses O(n). |
| 2 | Catalan DP composition | `O(C_n n)`. Every valid output is produced and copied; duplicate-free composition still emits C_n strings. | `O(C_n n)`. The DP table and final output store generated strings. |

## Pitfalls

- Never place more closing parentheses than opening parentheses in a prefix.
- Stop when the string length reaches 2n.
- Use a set or deterministic construction if combining subproblems can produce duplicates.
