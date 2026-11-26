# Strong Answer: Connect Four System

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Connect Four game, I will first clarify the requirements to establish our system's boundaries. Based on the problem statement, our core requirements include supporting two players alternating turns on a grid where discs fall to the lowest empty row. We need to handle deterministic terminal states (win or draw) and reject invalid moves. I will prioritize a clean separation between the game orchestration logic and the board mechanics to support testing and future extensions."

### Explicit Clarifications
- **Win Conditions**: 4 connected discs horizontally, vertically, or diagonally.
- **Game Flow**: Two players alternate turns. The game ends when a player wins or the board is full.
- **Failure Handling**: If a column is full, out of range, or a player acts out of turn, the move is invalid and rejected safely, leaving the game state unchanged.

## 2. Entity Modeling & Core Components (5-15 minutes)

**Say:** "Let's define the core entities and APIs. The `Game` orchestrates the match and enforces turn order. It interacts with the `Board` which strictly manages disc placement and win detection logic."

### Key Entities
| Entity | Responsibility |
|--------|---------------|
| `Game` | Turn control, state transitions, winner tracking |
| `Board` | Placement bounds, full checks, bounded win detection scans |
| `Player` | Name + disc color (`RED` or `YELLOW`) |
| `Move` | Immutable move history record |
| `BotMoveStrategy` | Bot column suggestion policy (v3) |
| `GameSession` | Session wrapper around one game instance (v3) |

### Public APIs
- **Make Move**: Java: `makeMove(Player player, int column)`, Python: `make_move(player: Player, column: int) -> bool`
  - Validates turn and column, places disc, updates history and terminal states.
- **Undo Last Move**: Java: `undoLastMove()`, Python: `undo_last_move() -> bool`
  - Pops move from history, clears cell on board, restores previous player and IN_PROGRESS state.
- **Suggest Bot Move**: Java: `suggestBotMove()`, Python: `suggest_bot_move() -> int`
  - Delegates to pluggable bot strategy to select a column.

## 3. Design Pattern Justifications (15-25 minutes)

**Say:** "To manage game history and bot decisions, I will utilize the **Command Pattern** conceptually via the Move history stack, and the **Strategy Pattern** for the bot."

### Design Alternatives
1. **Strategy Pattern for Bots**: By abstracting the `BotMoveStrategy`, we can swap out a `HeuristicBotMoveStrategy` for a Random or Minimax bot without modifying the core `Game` logic.
2. **Move History Stack vs Re-evaluating**: Storing a list of explicit `Move` objects provides O(1) undo operations, which is vastly superior to recreating the board state from scratch.

## 4. Correctness, Complexity & Acceptance Criteria (25-35 minutes)

**Say:** "Our solution ensures strict correctness across core operations. For instance, **normal use-cases** correctly transition turns and detect a 4-in-a-row win. **Empty/invalid inputs** (like selecting a full column) safely reject the action without altering state. **Duplicate operations** or acting out of turn are rejected safely. The system respects the **capacity boundary**; a slot cannot exceed its row limit. And **failure rollback** is handled via the undo API."

### Explicit Reference Contracts
To satisfy robustness guarantees, the system enforces the following explicit reference contracts natively in both Java and Python:
- **Normal Use-Case**: Player 1 plays column 0, player 2 plays column 1. State updates correctly. Four aligned discs trigger terminal WIN state.
- **Empty/Invalid Input**: Selecting a column out of bounds (<0 or >=cols) safely returns false without changing state.
- **Duplicate Operation**: A player attempting to move twice in a row (wrong turn) is safely rejected.
- **Capacity Boundary**: Attempting to place a disc in a column that is already full returns false.
- **Failure Rollback**: The `undoLastMove()` / `undo_last_move()` flow guarantees reverting the exact last move, restoring the turn and clearing the board cell.

## 5. Version-Specific Feature Deltas & Testing
The system evolves across iterations (Answer and source code version deltas agree):
- **v1-basic**: Fixed board size, two human players, core rules.
- **v2-extended**: Configurable board size and move history for undo capabilities.
- **v3-optimized**: Introduces pluggable bot strategies and a session wrapper.

**Testing Strategy**: Focused tests target the specific version (`v3-optimized`) rather than silently importing `v1`. The Python test suite isolates paths to target `v3-optimized`, and Java tests compile against the target directory to ensure strict version alignment.

## 6. Failure and Concurrency Discussion (35-45 minutes)

**Say:** "While a basic game might run single-threaded, a production online game session would require state synchronization."

### Concrete Discussion
- **Game Session State**: In a distributed setup, wrapping the `Game` in a `GameSession` allows us to serialize and persist the state easily. 
- **Concurrency**: If this were exposed via API, concurrent move submissions would need to be serialized (e.g. optimistic concurrency via version numbers) to prevent race conditions where two players appear to move at the same millisecond. 
- **Testing**: Deterministic tests prove bounded directional scans evaluate `O(1)` from the last placed disc instead of `O(rows*cols)`.

---

*This canonical answer directly maps to the `v3-optimized` implementations in both Java and Python.*
