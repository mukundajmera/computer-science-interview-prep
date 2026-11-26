# Strong Answer: Chess Game

## 45-Minute Pacing
A strong candidate focuses on building the core bounded 8x8 grid and validating primary piece movements first. Complex rules like *en passant*, castling, or pawn promotion are often best mentioned conceptually and stubbed initially, deferring them to an extended version unless the interviewer explicitly requires them.

## Explicit Clarifications
- **Scope**: The basic implementation covers standard movement, capturing, alternating turns, and boundary checking. 
- **Out of Scope**: Network sync, timers/clocks, and persistence layers. Draw by repetition or 50-move rules are also typically excluded from an initial 45-minute sprint.
- **Constraints**: 8x8 board, standard pieces. White always moves first.

## Entities and APIs
Derived from the merged reference codebase (`v1-basic`), with explicit version deltas across `v1-basic`, `v2-extended`, and `v3-optimized`.

| Entity | Responsibility |
|---|---|
| `Game` | Manages `Board`, tracks turns (`currentTurn`), and determines `GameState` (Active, Checkmate). Exposed API: `makeMove(from, to)`. |
| `Board` | Maintains the 8x8 grid of `Piece` references. Exposed APIs: `getPiece(Position)`, `setPiece(Position, Piece)`. |
| `Piece` | Abstract base class containing `Color`, `Position`, and `hasMoved`. Exposed API: `getValidMoves(Board)`. |
| `Position` | Represents algebraic or (row, column) coordinates on the grid. |

### Version-Specific Feature Deltas
| Feature | v1-basic | v2-extended | v3-optimized |
|---|---|---|---|
| Standard Piece Movement | Yes | Yes | Yes |
| Move History (`Move` class) | No | Yes | Yes |
| Check / Checkmate Detection | No | No | Yes |
| Board State Copy / Simulation | No | No | Yes |
## Design Alternatives
1. **Board Representation**: The reference uses a 2D array (`Piece[][]`). An alternative is using Bitboards (64-bit integers mapping piece locations), which offers extreme memory density and bitwise movement validation, but drastically increases code complexity. A 2D array is the expected standard for OOP interviews.
2. **Piece Instantiation and Rules**: The reference utilizes the **Factory Pattern** to create the pieces and the **Strategy Pattern** for movement logic (where each piece subclass encapsulates its own `isValidMove` rules). Alternatively, rule sets could be separated from piece states entirely, but the inheritance approach is standard.
3. **Turn Control**: The **State Pattern** can be implemented to track the `GameState` (Active, Check, Checkmate).

## Correctness and Complexity
- **Position Access**: Accessing a position via a 2D array `Board.getPiece(pos)` is **O(1)**.
- **Move Validation**: Simple pieces (King, Knight, Pawn) validate moves in **O(1)**. Sliding pieces (Rook, Bishop, Queen) scan paths, resulting in **O(N)** complexity where N ≤ 7 (max distance on an 8x8 board).
- **Check Detection**: Requires simulating or scanning all opposing pieces to see if any can attack the King's position, bounded by the maximum number of pieces (O(M) where M ≤ 16).

## Concrete Failure and Concurrency

### Reference Contracts for Edge Cases (v1-basic)
- **Normal Use-Case**: A valid move from a source position to an unoccupied destination position. Handled cleanly: `Game.makeMove(from, to)` (Java) or `game.make_move(from_pos, to_pos)` (Python) executes the move, updates piece states, and switches turns by returning `true` / `True`.
  - Java: `board.movePiece(from, to); currentTurn = currentTurn.opposite(); return true;`
  - Python: `self.board.move_piece(from_pos, to_pos); self.current_turn = self.current_turn.opposite(); return True`
- **Empty / Invalid Input**: Attempting a move from an empty square, or specifying coordinates outside the 8x8 grid bounds. Handled cleanly: `Game.makeMove(from, to)` (Java) or `game.make_move(from_pos, to_pos)` (Python) returns `false` / `False` if `board.getPiece(from)` / `board.get_piece(from_pos)` returns null/None. `Position.isValid()` (Java) or `Position.is_valid()` (Python) prevents out-of-bounds indexing.
  - Java: `if (piece == null) { return false; }` and `row >= 0 && row < 8 && col >= 0 && col < 8;`
  - Python: `if piece is None: return False` and `0 <= self.row < 8 and 0 <= self.col < 8`
- **Duplicate Operation**: Attempting to move the same piece out of turn. Validated by `piece.getColor() != currentTurn` (Java) or `piece.color != self.current_turn` (Python), immediately returning `false` / `False`.
  - Java: `if (piece.getColor() != currentTurn) { return false; }`
  - Python: `if piece.color != self.current_turn: return False`
- **Capacity Boundary**: The board is strictly bounded to an 8x8 grid structure. Memory usage and piece count are capped naturally by the fixed dimensions (maximum 32 pieces).
  - Java: `Piece[][] grid = new Piece[8][8];`
  - Python: `self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]`
- **Failure Rollback**: In standard operations, invalid moves return `false` / `False` before modifying state. For advanced speculative validations (e.g., preventing a move that leaves the King in check), the system creates a copy of the board, executes the move temporarily, and if invalid, rolls back by discarding the copy and rejecting the move.
  - Java: `Board copy = board.copy(); copy.movePiece(from, to); if (copy.isCheck(currentTurn)) return false;`
  - Python: `board_copy = self.board.copy(); board_copy.move_piece(from_pos, to_pos); return False if board_copy.is_check(self.current_turn) else True`

### Public APIs and Feature Deltas
- The `v1-basic` implementation provides foundational chess mechanics. The public API surface includes:
  - Game control: `makeMove` / `make_move`, `getValidMoves` / `get_valid_moves`
  - Board access: `getPiece` / `get_piece`, `setPiece` / `set_piece`
- Tests are version-scoped and explicitly import the `v1-basic` or `v3-optimized` modules (e.g., importing `from v3_optimized.game import Game` in Python or running the `v3-optimized` package in Java) to ensure version-specific features are accurately validated against the active implementation context, rather than bleeding across version boundaries.


### Concurrency
In a concurrent environment (e.g., if exposed as a web service API), `Game.makeMove` must be atomic (synchronized on the `Game` instance or employing lock-striping on specific squares) to prevent two players from simulating overlapping board states at the same time.
