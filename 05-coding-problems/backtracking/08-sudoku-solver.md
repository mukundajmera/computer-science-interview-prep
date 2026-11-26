# Sudoku Solver

## Overview

Given a partially filled `9 x 9` Sudoku board, fill every empty cell so each row, column, and `3 x 3` box contains digits `1` through `9` without duplicates.

This is constraint satisfaction with backtracking.

## Requirements and constraints

- Mutate the board in place or return a solved board, depending on prompt wording.
- Respect row, column, and box constraints.
- Stop after one valid solution unless the prompt asks for all solutions.
- Restore cells and constraint state when a candidate fails.

## Recognition cue

"Fill a board under row, column, and subgrid constraints" signals constraint-propagation backtracking.

## Invariant or state definition

Before each recursive call, every filled cell respects Sudoku constraints, and every empty cell remains available for assignment.

## High-level design / approach

1. Preload row, column, and box sets from the initial board.
2. Collect empty cells.
3. Choose the next empty cell.
4. Try digits `1` through `9`.
5. Skip digits already present in the row, column, or box.
6. Place a digit, update sets, recurse.
7. If recursion succeeds, return true.
8. Otherwise undo the digit and continue.

## Dry run

For an empty cell at `(0,2)`:

| Constraint | Existing digits | Candidate impact |
|---|---|---|
| row `0` | `5, 3, 7` | cannot use `5, 3, 7` |
| column `2` | `8` | cannot use `8` |
| box `(0,0)` | `5, 3, 6, 9, 8` | cannot use those |

Legal candidates are digits not present in any of the three sets. Try one, recurse, and undo if it leads to a dead end.

## Language-neutral pseudocode

```text
rows, cols, boxes = preload constraints
empties = list of empty cells

solve(pos):
    if pos == empties.length:
        return true

    r, c = empties[pos]
    b = box_id(r, c)
    for digit in "1".."9":
        if digit in rows[r] or digit in cols[c] or digit in boxes[b]:
            continue
        place digit on board
        add digit to rows[r], cols[c], boxes[b]
        if solve(pos + 1):
            return true
        remove digit from rows[r], cols[c], boxes[b]
        reset board[r][c] to empty
    return false
```

## Complexity

- Time: worst-case exponential, often expressed as `O(9^E)` where `E` is the number of empty cells, reduced by constraints.
- Space: `O(E)` recursion depth plus constraint sets.
- The board size is fixed at `9 x 9` in classic Sudoku, so practical bounds are constrained, but the search remains exponential in empty cells.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Constraint sets | Tracks rows, columns, and boxes |
| Box math | Computes box id consistently |
| Backtracking | Restores board and sets after failed candidates |
| Stop condition | Returns true after filling every empty cell |

## Common pitfalls

1. Forgetting `3 x 3` box constraints.
2. Leaving a failed digit on the board.
3. Continuing after finding one solution when the prompt asks to solve in place.
4. Recomputing full row/column scans without explaining the trade-off.

## Follow-up questions

1. How would you pick the next cell with the fewest candidates?
2. How would you detect an invalid starting board?
3. How would you return all solutions instead of one?

## Variants and extensions

- Minimum-candidate heuristic.
- Sudoku validator.
- Larger `n x n` Sudoku variants.
- Constraint solver for scheduling or placement.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [N-Queens](./07-n-queens.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
