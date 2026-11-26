# Valid Sudoku

## Clean-Room Summary

Determine whether a partially filled 9x9 Sudoku board currently respects the row, column, and 3x3 box uniqueness rules.

## Driver Signature

```java
class Solution {
    public boolean isValidSudoku(char[][] board) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Case | Expected |
|---|---|
| Sparse board with no repeated digit in any unit | `true` |
| A row, column, or 3x3 box repeats a digit | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Scan rows, columns, and boxes separately with sets | `O(1)`. | `O(1)`. |
| 2 | Single pass with row, column, and box bitmasks | `O(1)`. | `O(1)`. |

## Pitfalls

- Skip empty cells when checking duplicates.
- Convert each digit to a stable index before using bitmasks.
- A board can be valid so far even if it is not solved.
