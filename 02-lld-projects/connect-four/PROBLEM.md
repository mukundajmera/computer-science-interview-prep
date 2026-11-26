# Connect Four

## Problem Statement
Design and implement the backend object model for a two-player Connect Four game.

## Requirements and constraints

### Functional requirements
1. Two players take turns dropping discs into columns of a board.
2. Standard board is 6 rows x 7 columns for v1.
3. A disc occupies the lowest empty row in the selected column.
4. Reject invalid moves:
- column out of range
- full column
- wrong player turn
- move after game has ended
5. Detect terminal states:
- win: four connected discs horizontally, vertically, or diagonally
- draw: board full with no winner

### Non-functional requirements
- Deterministic game behavior for tests.
- Clear separation between orchestration (`Game`) and grid logic (`Board`).
- Java and Python parity across all versions.
- Standard-library-only implementation.

## Out of scope
- UI rendering
- network multiplayer
- matchmaking and persistence

## Version roadmap
- **v1-basic:** fixed board size, two human players, core rules.
- **v2-extended:** configurable board size and undo/move history.
- **v3-optimized:** pluggable bot strategy and session wrapper.

## Related content
- [Tic-Tac-Toe](../tic-tac-toe/)
- [State Pattern](../../01-design-patterns/behavioral/state/)
- [Command Pattern](../../01-design-patterns/behavioral/command/)
