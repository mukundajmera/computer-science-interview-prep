# Chess Game — Follow-Up Questions

Use these variants to drive deeper interview discussion after the baseline design.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. How would you implement an "Undo" feature?
- **Model Answer**: Implement the Command Pattern. Each move is a command object with an `execute()` and `undo()` method. Maintain a stack of executed moves. Popping from the stack and calling `undo()` restores the previous board state.

## 2. How to support a game replay or PGN export?
- **Model Answer**: Since we have a move history (via Command pattern), iterate through the moves and serialize them into standard algebraic notation (PGN).

## 3. How would you optimize the game for a chess AI (Minimax)?
- **Model Answer**: Object-oriented designs (classes for pieces) are too slow for deep tree searches. I would discuss refactoring to use **Bitboards** (64-bit integers) representing piece locations, allowing ultra-fast bitwise operations for move generation.

## 4. How to handle pawn promotion flexibly?
- **Model Answer**: When a pawn reaches the last rank, the `MoveCommand` triggers an event to the UI requesting user input. The core engine pauses state until a piece type is injected back, replacing the pawn object.

## 5. How would you implement a networked multiplayer mode?
- **Model Answer**: The core game engine sits on the server. Clients send action requests (moves). The server validates the move, updates state, and broadcasts the new state/move event to both clients via WebSockets.

## 6. How do you detect a Stalemate or Draw by repetition?
- **Model Answer**: For stalemate: check if the current player has zero valid moves AND the King is not in check. For repetition: maintain a hash map of board state hashes (Zobrist hashing) and count occurrences.

## 7. How to implement timing constraints (e.g., Blitz chess)?
- **Model Answer**: Integrate a `GameTimer` component. It uses background threads or async tasks to count down the active player's clock. If a clock hits zero, it triggers a "Time Out" event to the `GameController`, ending the game.

## 8. What is your strategy for persisting a game in progress to a database?
- **Model Answer**: Serialize the board state (e.g., using FEN notation) and the list of executed moves. Store this in a relational database with GameID, PlayerIDs, and current turn status.

## 9. How would you handle spectator mode?
- **Model Answer**: Use a Pub/Sub model. The `GameController` publishes move events to a specific game topic. Spectator clients subscribe to this topic via WebSockets to receive read-only real-time updates.

## 10. How to handle custom chess variants (e.g., Fischer Random / Chess960)?
- **Model Answer**: Use the Factory pattern or Builder pattern for board setup. Abstract the initial piece placement logic so a variant rule engine can inject a randomized, yet valid, starting configuration.

---

## Follow-Up Scoring Signals

1. Candidate explains trade-offs, not only feature lists.
2. Candidate preserves API boundaries while extending behavior.
3. Candidate understands the performance implications of OO design vs bitboards for AI.
