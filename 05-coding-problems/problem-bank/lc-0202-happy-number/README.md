# Happy Number

## Clean-Room Summary

Repeatedly replace a number with the sum of squared digits and decide whether the process reaches one.

## Driver Signature

```java
class Solution {
    public boolean isHappy(int n) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def isHappy(self, n: int) -> bool:
        # implementation
```

## Repo-Authored Examples

| n | happy |
| ---: | --- |
| `7` | `true` |
| `4` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Seen set cycle detection | `O(log n)`. | `O(log n)`. |
| 2 | Floyd cycle detection | `O(log n)`. | `O(1)`. |

## Pitfalls

- A repeated value means the process is cycling away from one.
- Digit-square transformation should handle all decimal digits.
- Floyd cycle detection avoids storing the seen set.
