# Evaluate Reverse Polish Notation

## Clean-Room Summary

Evaluate an arithmetic expression written in reverse Polish notation using integer operations.

## Driver Signature

```java
class Solution {
    public int evalRPN(String[] tokens) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        # implementation
```

## Repo-Authored Examples

| tokens | value |
| --- | ---: |
| `["6", "2", "/", "3", "+"]` | `6` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Stack evaluator | `O(n)`. | `O(n)`. |

## Pitfalls

- Operators consume the two most recent operands in left-then-right order.
- Division truncates toward zero.
- Negative numeric tokens are operands, not operators.
