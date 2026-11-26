# N-Queens

## Overview

Place `n` queens on an `n x n` chessboard so that no two queens attack each other.

Backtracking places one queen per row and maintains constraint sets for occupied columns and diagonals.

## Requirements and constraints

- Return all valid boards or the count, depending on the prompt.
- Place exactly one queen in every row.
- Queens cannot share a column, major diagonal, or minor diagonal.
- Preserve board state across sibling branches by undoing placements.

## Recognition cue

"Place pieces under row, column, and diagonal constraints" signals constraint-placement backtracking.

## Invariant or state definition

At recursive row `r`, rows `0` through `r - 1` each contain one queen, and no placed queens attack each other.

## High-level design / approach

1. Track occupied columns.
2. Track major diagonals by `row - col`.
3. Track minor diagonals by `row + col`.
4. For the current row, try every column.
5. Skip columns whose constraints are occupied.
6. Place the queen, update sets, recurse to the next row, then undo.
7. Emit a copied board when `row == n`.

## Dry run

For `n = 4`, one successful placement path is:

| Row | Chosen column | Constraints added |
|---|---:|---|
| 0 | 1 | column `1`, diagonals `-1`, `1` |
| 1 | 3 | column `3`, diagonals `-2`, `4` |
| 2 | 0 | column `0`, diagonals `2`, `2` |
| 3 | 2 | column `2`, diagonals `1`, `5` |

Board:

```text
.Q..
...Q
Q...
..Q.
```

## Language-neutral pseudocode

```text
results = []
board = n x n filled with "."
cols = set()
diag1 = set()   // row - col
diag2 = set()   // row + col

dfs(row):
    if row == n:
        results.add(copy_board(board))
        return

    for col in 0..n-1:
        if col in cols or row - col in diag1 or row + col in diag2:
            continue
        place queen at row, col
        add col, row - col, row + col
        dfs(row + 1)
        remove col, row - col, row + col
        remove queen from row, col
```

## Complexity

- Time: exponential, commonly bounded by `O(n!)` candidate placements with pruning, with board-copy cost for each solution.
- Space: `O(n)` recursion and constraint sets, plus board representation and output.
- Output size depends on the number of valid boards.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Row strategy | Places one queen per row |
| Constraints | Uses column and both diagonal sets |
| Diagonal math | Correctly uses `row - col` and `row + col` |
| Restore | Removes queen and all constraints after recursion |

## Common pitfalls

1. Checking only columns and missing diagonals.
2. Mixing up diagonal formulas.
3. Reusing the same board reference in results.
4. Scanning the whole board for conflicts instead of using sets.

## Follow-up questions

1. How would you return only the number of solutions?
2. How can bitmasks speed up constraint checks?
3. What changes for blocked cells?

## Variants and extensions

- N-Queens II count-only.
- Bitmask N-Queens.
- Constraint placement with blocked cells.
- Resource placement across zones with conflict rules.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [Sudoku Solver](./08-sudoku-solver.md)
- [Workflow Orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
