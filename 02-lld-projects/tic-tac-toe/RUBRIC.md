# Tic-Tac-Toe - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies 3x3 versus N x N, two-player scope, mark assignment, undo, AI, and reset behavior |
| Core modeling | 20% | Separates `Game`, `Board`, `Player`, `Position`, `Move`, `Mark`, and `WinChecker` responsibilities |
| Move and state correctness | 25% | Rejects out-of-bounds, occupied-cell, wrong-state, and post-game moves while alternating turns correctly |
| Win/draw detection | 25% | Checks only the affected row, column, and diagonals for O(N) detection and handles full-board draw |
| Extensibility and communication | 15% | Explains v1 to v3 progression, command-style undo, AI strategy, and multi-session thread-safety scope |

## Performance bands
- `1/5`: procedural 3x3 board with weak validation and duplicated win checks.
- `3/5`: clean two-player game with state transitions, win/draw detection, and basic reset.
- `5/5`: extensible N x N design with move history, AI strategy hooks, optimized win checks, and tested edge cases.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
