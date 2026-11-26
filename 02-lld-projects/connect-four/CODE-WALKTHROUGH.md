# Connect Four Code Walkthrough

## Typical move flow
1. Caller invokes `Game.makeMove(player, column)`.
2. `Game` validates turn, game state, and board capacity.
3. `Board.placeDisc` computes landing row and mutates grid.
4. `Board.checkWin` evaluates four directional lines crossing last disc.
5. `Game` updates to `WON`, `DRAW`, or flips turn.

## Undo flow (v2)
1. Successful move pushes `Move` to history stack.
2. `undoLastMove()` pops latest move.
3. `Board.clearCell(row, column)` removes disc.
4. `Game` resets terminal flags and restores current player.

## Bot flow (v3)
1. `Game.suggestBotMove()` delegates to `BotMoveStrategy`.
2. Strategy checks immediate winning/blocking opportunities.
3. Fallback picks first legal column deterministically.

## Validation checkpoints
- Wrong-turn moves return `false`.
- Full column moves return `false`.
- Board-full without winner sets `DRAW`.
