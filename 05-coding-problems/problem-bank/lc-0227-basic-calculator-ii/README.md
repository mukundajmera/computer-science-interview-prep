# Basic Calculator II

## Clean-Room Summary

Evaluate an expression containing non-negative integers, spaces, and the four basic operators with multiplication and division precedence.

## Driver Signature

```java
class Solution {
    public int calculate(String s) {
        // implement
    }
}
```

```python
class Solution:
    def calculate(self, s: str) -> int:
        # implement
```

## Repo-Authored Cases

- `multiplication before addition`
- `division truncates`
- `mixed spaces and division`
- `subtraction with product`
- `multi digit chain`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Stack terms | `O(n)`. The expression string is scanned once. | `O(n)`. The stack can store one term for each additive segment. |
| 2 | Rolling last term | `O(n)`. Each character is scanned once. | `O(1)`. Only the current number, last term, and total are stored. |

## Pitfalls

- Division truncates toward zero, not toward negative infinity.
- Process the final number after the scan even when the expression does not end with an operator.
