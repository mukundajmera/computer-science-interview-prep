# Connect Four Design

## Core entities

| Entity | Responsibility |
|---|---|
| `Game` | Turn enforcement, terminal-state transitions, winner tracking |
| `Board` | Disc placement, bounds/full checks, win detection |
| `Player` | Identity and disc color |
| `Move` (v2+) | Immutable move record for undo/history |
| `BotMoveStrategy` (v3+) | Bot column selection policy |

## Key APIs

### `Game`
- `makeMove(player, column) -> bool`
- `getCurrentPlayer() -> Player`
- `getGameState() -> GameState`
- `getWinner() -> Player?`
- `undoLastMove() -> bool` (v2+)
- `suggestBotMove() -> int` (v3+)

### `Board`
- `canPlace(column) -> bool`
- `placeDisc(column, color) -> int`
- `checkWin(row, column, color) -> bool`
- `isFull() -> bool`
- `clearCell(row, column)` (v2+)

## Invariants
1. Only current player can move.
2. No state mutation after `WON` or `DRAW`.
3. `placeDisc` never overwrites occupied cells.
4. Undo restores both board and turn order.

## Complexity
- `placeDisc`: O(rows)
- `checkWin`: O(1) for fixed 4 directions from last move
- `undoLastMove`: O(1)
