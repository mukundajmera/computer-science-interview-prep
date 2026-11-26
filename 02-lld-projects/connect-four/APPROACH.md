# Approach for Connect Four

## Overview and Core Strategy
Designing a low-level implementation of Connect Four requires a focus on decoupling the turn-based state machine from the grid mechanics. The system is designed to provide strict encapsulation, allowing for normal gameplay, robust rejection of invalid inputs, and a flexible architecture to support extensions like an undo feature and bot play without polluting the core logic. 

Our approach separates concerns by isolating turn management and game termination rules in the `Game` class, while delegating raw spatial logic and disc gravity to the `Board` class. This allows the state and physics of the game to evolve independently.

## API Contracts and Edge Case Handling
The system exposes a rigid interface that cleanly enforces the rules. The primary API is `Game.makeMove(Player, int) -> boolean` (Java) / `Game.make_move(Player, int) -> bool` (Python). This method acts as the transaction boundary for a single turn. It guarantees determinism by strictly enforcing invariants:
1. **Normal Use-Case:** A valid move by the `currentPlayer` in an available column drops the disc to the lowest empty row and toggles the turn.
2. **Empty/Invalid Input:** Columns that are out-of-bounds (e.g., `< 0` or `>= cols`) immediately return `false` without state mutation.
3. **Duplicate/Wrong Turn:** If a player attempts to move out of turn, or if `makeMove` is called with the wrong player object, it is rejected.
4. **Capacity Boundary:** If a specific column is full, or if the entire board is full (resulting in a DRAW), the move is correctly handled. A full column rejects the move, while filling the last slot on the board correctly transitions the game state to `DRAW`.
5. **Failure Rollback:** If `placeDisc` fails internally for any reason after initial validation, the turn is not consumed, and the game state remains identical to before the call.

## State Management and Win Detection
The `Board` is implemented using a 2D array (`DiscColor[][]` in Java, `list[list[DiscColor]]` in Python), initialized to `EMPTY`. This straightforward spatial representation is robust for the specified board size (6x7 in v1, configurable in v2) and makes tracking exact coordinates simple.

The win detection algorithm evaluates the state exactly around the newly placed disc. Instead of scanning the entire board, `checkWin(row, col, color)` operates in O(1) time relative to the board size by checking a maximum of 4 directions (horizontal, vertical, two diagonals) outward from the specific `(row, col)` coordinate just played.

## Version-Specific Feature Deltas
To support evolving requirements, the system iterates through versions without backwards pollution:
- **`v1-basic`:** Implements the core rules with a fixed 6x7 board, turn enforcement, and win/draw detection using `GameState`.
- **`v2-extended`:** Enhances `Board` to be configurable (e.g., dynamically sized beyond 6x7). Introduces the `Move` class and `undoLastMove() -> boolean` on `Game`, allowing state rollback by tracking a history stack of moves.
- **`v3-optimized`:** Abstracts player strategies with `BotMoveStrategy`. Introduces `HeuristicBotMoveStrategy` which evaluates immediate winning moves or blocks for the opponent before falling back to the first available column. It adds `GameSession` as a higher-level orchestrator and `suggestBotMove()` to integrate automated decision-making.

By using standard data structures and avoiding global state, both the Java and Python implementations maintain full parity and are fully deterministically testable in isolation. Tests must explicitly target version-specific directories rather than silently importing v1.
