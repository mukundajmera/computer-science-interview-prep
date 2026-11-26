# Sudoku Solver

- Canonical ID: `lc-0037-sudoku-solver`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Fill every empty cell in a 9 by 9 Sudoku board so each row, column, and 3 by 3 box contains each digit at most once.

## Driver Signature

- Java: `void solveSudoku(char[][] board)`
- Python: `solveSudoku(board: List[List[str]]) -> None`

## Key Cases and Invariants

- The board is mutated in place and the method returns no value.
- A candidate digit must be valid across row, column, and box simultaneously.
- Tracking candidate availability avoids rescanning the whole board for every trial.

## Solution Ladder

### Tier 1: Naive backtracking

Find the next empty cell, try digits, and rescan row/column/box to test validity.

- Time: `O(9^E * 9)` - In the worst case E blanks branch over digits and each validity check scans fixed-size lines.
- Space: `O(E)` - Recursion depth is the number of empty cells.

### Tier 2: Bitmask backtracking

Maintain row, column, and box digit masks so candidate checks and updates are constant time.

- Time: `O(9^E)` - Backtracking still explores candidates, but validity checks are O(1).
- Space: `O(E)` - Masks are fixed-size and recursion depth is E.
