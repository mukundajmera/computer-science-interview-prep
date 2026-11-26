# Tic-Tac-Toe - Common Pitfalls

## Common pitfalls
1. Checking the whole board after every move instead of using the last move's row, column, and diagonals.
2. Letting the board place marks without the game enforcing turn order and game state.
3. Treating `EMPTY` as a player mark and accidentally allowing it to win.
4. Implementing undo by clearing a cell but not restoring current player, move history, or game state.
5. Adding minimax before the basic game contract is stable and well tested.

## Why these fail interviews
- They blur the boundary between board storage and game orchestration.
- They produce subtle state bugs after win, draw, reset, or undo.
- They make N x N support and AI search harder than necessary.

## Mitigations
- Keep `Board` focused on cell storage and validation; keep turn/state transitions in `Game`.
- Store every accepted move and derive undo from that history.
- Pass the last move into `WinChecker` so it only checks relevant lines.
- Add AI as a player strategy after the human game loop is correct.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
