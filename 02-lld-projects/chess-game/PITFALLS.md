# Chess Game — Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Mixing UI and Game Logic
- **Pitfall**: The `Board` or `Piece` classes handle rendering (e.g., drawing to console or GUI).
- **Why it hurts**: Violates SRP; makes the core game engine impossible to use across different platforms (web, mobile, CLI).
- **Better**: Keep game logic strictly headless. Use the Observer pattern to notify UI components of state changes.

## 2. Bloated Board Class
- **Pitfall**: Putting all move validation, checkmate detection, and turn management inside the `Board` class.
- **Why it hurts**: Creates a massive God class that is difficult to test and maintain.
- **Better**: Separate concerns. `Board` should only manage the grid. Delegate rules to a `GameController` or `MoveValidator`.

## 3. Ignoring Special Moves Early On
- **Pitfall**: Designing the architecture without considering castling, en passant, or pawn promotion.
- **Why it hurts**: These rules require historical state (e.g., "has the king moved?"). Adding them later often requires painful refactoring.
- **Better**: Design the state model to include move history and specific piece flags from the beginning.

## 4. Inefficient Move Validation
- **Pitfall**: Validating check/checkmate by creating deep copies of the entire board for every possible move.
- **Why it hurts**: Extremely slow, especially if you ever want to implement an AI.
- **Better**: Use a make/unmake move approach, or use more advanced bitboard representations if performance is critical.

## 5. Poor Piece Abstraction
- **Pitfall**: Using a giant switch statement in a single `Piece` class to determine how it moves.
- **Why it hurts**: Violates the Open/Closed Principle. Hard to read and extend.
- **Better**: Make `Piece` an abstract base class with a `getValidMoves()` method overridden by specific piece subclasses (Strategy pattern).

## 6. Lack of a Move History
- **Pitfall**: Overwriting the board state without keeping a log of moves.
- **Why it hurts**: Prevents implementing "undo", move replays, or the fifty-move draw rule.
- **Better**: Implement the Command Pattern for moves, storing an ordered list of `MoveCommand` objects.

## 7. Hardcoding Board Dimensions
- **Pitfall**: Hardcoding 8x8 loops everywhere in the code.
- **Why it hurts**: Makes the code brittle and prevents adapting to variants on different board sizes.
- **Better**: Define constants for board dimensions and use dynamic checks.

## 8. Checking for 'Check' Incorrectly
- **Pitfall**: Trying to calculate if a King is in check by looking at the King's perspective only.
- **Why it hurts**: Misses complex discovery attacks or pins.
- **Better**: Check if the King's square is under attack by *any* enemy piece by generating all enemy attack vectors.
