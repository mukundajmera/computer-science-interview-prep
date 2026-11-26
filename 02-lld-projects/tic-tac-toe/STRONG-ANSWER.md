# Strong Answer: Tic-Tac-Toe Game

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Clarification (0-5 minutes)

**Say:** "To design the Tic-Tac-Toe Game, I will focus on a clear separation of concerns, modeling the core game mechanics independently from player interaction or game orchestration. I'll outline the core data models like `Board` and `Game`, discuss handling constraints such as invalid moves or capacity boundaries, and then walk through the optimizations for AI and concurrent sessions. My goal is an extensible design that can support variations in board size or rules."

By clarifying upfront, we frame the design around deterministic logic and strict state transitions. The functional requirements define a system that accepts moves and accurately resolves game states (win/draw), while non-functional requirements push us to optimize win detection (O(1) updates vs full scans) and handle concurrency for a multi-game server environment.

## 2. Entity Modeling & Core Components (5-15 minutes)

**Say:** "The core entities in our design are the `Game`, `Board`, `Player`, `WinChecker`, and `GameSession`.
- **`Board`**: Encapsulates the N×N grid, tracking marks (`X`, `O`, `EMPTY`) and the count of empty cells to quickly identify draws. It acts as a passive data structure.
- **`Player`**: An abstract base class defining `makeMove(Board)`, with concrete implementations like `HumanPlayer` and `AIPlayer`.
- **`WinChecker`**: Separates the win evaluation logic from the `Board`. Instead of a naive O(N²) scan, it uses an O(N) strategy bounded to the `lastMove`. 
- **`Game`**: The central orchestrator. It manages the `Board`, the two `Players`, the `currentPlayerIndex`, and uses `WinChecker` to transition the `GameState` (`IN_PROGRESS`, `X_WON`, `DRAW`)."

Using `GameState` as an explicit enum ensures that terminal states are rigidly enforced. By separating `Board` mechanics from `Game` orchestration, we adhere to the Single Responsibility Principle, setting the stage for future rule modifications, such as different win conditions, via the Strategy pattern.

## 3. APIs and Version Deltas (15-25 minutes)

**Say:** "Our public API centers around the `Game` class orchestrating the interaction:
- `boolean Game.makeMove(Position)`: Validates the move, updates the board, and transitions the state if necessary.
- `void Game.play()`: Executes the game loop, fetching moves from the current player.

As the implementation evolves through versions, feature deltas emerge:
- **v1-basic**: Implements the core game loop, abstract `Player`, and naive `WinChecker` that scans the board.
- **v2-extended**: Introduces `Move` history (Command Pattern) allowing for undo capabilities, and an `AIPlayer` using basic Minimax.
- **v3-optimized**: Introduces a `GameSession` manager for multi-game concurrent hosting, `GameFlowCoordinator` for abstract rule coordination, and Alpha-Beta pruning in the `AIPlayer` to handle larger N×N boards efficiently."

Focused testing ensures reliability. To maintain clarity, our public APIs and version-specific feature deltas are heavily documented. To prevent regression, our focused test suite strictly targets this specific version's isolated components rather than silently importing standard code from the earlier v1 baseline. Tests in `TestBoard` ensure out-of-bounds `Position`s and full cells are rejected, while `TestWinChecker` validates horizontal, vertical, and diagonal win combinations using deterministic scenarios.

## 4. Normal Use-Cases and Edge Cases (25-35 minutes)

**Say:** "Let's trace the normal use-case and edge cases:
- **Normal Play**: Player X submits a `Position(0,0)`. `Game.makeMove()` verifies `GameState.IN_PROGRESS`, delegates to `Board.placeMark()`, and calls `WinChecker.checkWin()`. The state transitions if X wins, else it toggles the active player.
- **Empty/Invalid Input**: If a player submits an out-of-bounds position (e.g., -1, 0) or attempts to overwrite an occupied cell, `Board.placeMark()` returns false. `Game.makeMove()` rejects the attempt gracefully, requiring the player to retry.
- **Duplicate Operation**: If a client attempts to submit a move after the game has reached `X_WON`, `O_WON`, or `DRAW`, `makeMove()` immediately fails, preserving the immutable terminal state.
- **Capacity Boundary**: A naive Minimax AI evaluating a 4×4 or larger board faces an exponential state space explosion (O(b^d)). In **v3-optimized**, we hit this boundary and mitigate it by employing Alpha-Beta pruning in the `AIPlayer`, aggressively culling unpromising branches and incorporating an evaluation heuristic for early depth cut-offs."

Our robust design explicitly mitigates runtime failures and handles capacity limits gracefully. As proven by our test suite, normal use-case, empty/invalid input, duplicate operation, capacity boundary and one failure rollback match an explicit reference contract in both languages. Determinism in checking validity protects the board state, ensuring corrupt inputs do not crash the session.

## 5. Concurrency and Failure Rollbacks (35-45 minutes)

**Say:** "When extending to a server hosting multiple games (**v3-optimized**), we introduce the `GameSession` manager. It tracks active games using a `ConcurrentHashMap<String, Game>`. 

For concurrency:
- Creating a game requires coordination. `GameSession.createGame()` is `synchronized` to ensure atomic incrementation of the `gameCounter` and safe insertion into the map.
- If two clients attempt a move on the same `Game` concurrently, the `Game` state is currently not inherently thread-safe. A true distributed deployment would require a `ReentrantLock` on the `Game` instance to serialize `makeMove()` operations, ensuring strict turn enforcement.

For failure rollbacks, consider a scenario where a distributed move involves persisting the move to a database. If the database commit fails, we must rollback the in-memory board state. We can achieve this by invoking `Board.removeMark(lastMove)` and reverting the `currentPlayerIndex`, effectively restoring the pre-move snapshot to maintain absolute consistency."

By discussing concurrent maps and explicit locking, we demonstrate an understanding of multi-threading risks in Java. The rollback scenario provides a concrete failure trace, proving the system can recover from partial distributed failures.

