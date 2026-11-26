# Design Approach for Chess Game

A step-by-step thought process for designing the chess game.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Game | ✅ Yes | Main controller |
| Board | ✅ Yes | Game state container |
| Piece | ✅ Yes | Abstract base for piece types |
| Player | ✅ Yes | Participant in game |
| Move | ✅ Yes | Action representation |
| Square/Position | ✅ Yes | Location on board |
| Color | ❌ No | Enum/attribute |

**Final Entities**: Game, Board, Piece (+ subclasses), Player, Move, Position

---

## Step 2: Define Relationships

```
Game (1) ──manages──> (1) Board
Game (1) ──has──> (2) Player
Board (1) ──contains──> (n) Piece
Piece (1) ──occupies──> (0..1) Position
Player (1) ──owns──> (n) Piece
Move (1) ──references──> (1) Piece
Move (1) ──references──> (2) Position (from, to)
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| Game → Board | Composition | Board belongs to game |
| Board → Piece | Aggregation | Pieces can be captured/removed |
| Player → Piece | Association | Player controls pieces |
| Move → Position | Association | Move references positions |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Factory** | ✅ Yes | Create different piece types |
| **Strategy** | ✅ Yes | Movement rules per piece |
| **Command** | ✅ v2 | Move history for undo |
| **State** | ✅ v3 | Game states (playing, check, checkmate) |

### Pattern Application:

1. **Factory Pattern** - PieceFactory
   - Creates King, Queen, Rook, Bishop, Knight, Pawn
   - Encapsulates piece creation logic

2. **Strategy Pattern** - MovementStrategy
   - Each piece type has its own movement rules
   - Easily extensible for new pieces

3. **Command Pattern** - MoveCommand (v2)
   - Each move is a command object
   - Supports undo/redo operations

4. **State Pattern** - GameState (v3)
   - Playing, Check, Checkmate, Stalemate, Draw
   - State transitions based on moves

---

## Step 4: Design Classes

### Core Classes:

#### Game
- **Attributes**: 
  - `board: Board`
  - `players: Player[2]`
  - `currentTurn: Color`
  - `gameState: GameState`
  - `moveHistory: List<Move>`
- **Methods**:
  - `makeMove(from, to): boolean`
  - `getValidMoves(position): List<Position>`
  - `isGameOver(): boolean`
  - `getCurrentPlayer(): Player`

#### Board
- **Attributes**:
  - `squares: Piece[8][8]`
- **Methods**:
  - `getPiece(position): Piece`
  - `setPiece(position, piece): void`
  - `removePiece(position): Piece`
  - `isValidPosition(position): boolean`
  - `findKing(color): Position`

#### Piece (Abstract)
- **Attributes**:
  - `color: Color`
  - `position: Position`
  - `hasMoved: boolean`
- **Methods**:
  - `getValidMoves(board): List<Position>` (abstract)
  - `canMoveTo(board, target): boolean`
  - `getSymbol(): char`

#### Player
- **Attributes**:
  - `name: String`
  - `color: Color`
- **Methods**:
  - `getColor(): Color`

#### Move
- **Attributes**:
  - `piece: Piece`
  - `from: Position`
  - `to: Position`
  - `capturedPiece: Piece`
  - `isSpecialMove: boolean`
- **Methods**:
  - `execute(board): void`
  - `undo(board): void`

#### Position
- **Attributes**:
  - `row: int` (0-7)
  - `col: int` (0-7)
- **Methods**:
  - `isValid(): boolean`
  - `toAlgebraic(): String` (e.g., "e4")

---

## Step 5: Handle Edge Cases

### Input Validation:
- Invalid positions (outside board)
- Moving opponent's piece
- Moving to same position
- Null piece selection

### Game Logic:
- Cannot move into check
- Must escape check if in check
- Cannot castle through check
- En passant only immediately after opponent's pawn move
- Pawn promotion choice

### Concurrency (v3):
- Multiple clients viewing same game
- Move submission race conditions

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Find piece at position | O(1) | O(1) - 2D array |
| Find all pieces of color | O(64) | O(16) - piece lists |
| Check detection | O(64) | O(n) - attacker iteration |

### Caching:
- Cache valid moves per piece (invalidate on move)
- Cache king positions for quick check detection

---

## Step 7: Version Progression

### v1-basic
- Board with 2D array
- All piece types with basic movement
- Turn management
- Simple capture
- ~400-500 lines

### v2-extended
- Castling, en passant, pawn promotion
- Move history with command pattern
- Undo functionality
- Algebraic notation
- ~600-800 lines

### v3-optimized
- Check and checkmate detection
- Stalemate and draw conditions
- Move validation considers check
- Game state management
- ~800-1000 lines

---

## Code Organization

```
chess-game/
├── java/
│   ├── v1-basic/
│   │   ├── Game.java           # Main game controller
│   │   ├── Board.java          # 8x8 board
│   │   ├── Piece.java          # Abstract piece + subclasses
│   │   ├── Position.java       # Board position
│   │   ├── Color.java          # Enum
│   │   └── ChessDemo.java      # Usage example
│   ├── v2-extended/
│   │   ├── Move.java           # Command pattern
│   │   └── [Enhanced versions]
│   └── v3-optimized/
│       └── [Check/checkmate detection]
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why abstract Piece class?**
   - Common attributes (color, position)
   - Polymorphic movement validation
   - Factory pattern integration

2. **How to efficiently detect check?**
   - Find king position
   - Check if any opponent piece can attack king
   - Can optimize with attack tables

3. **Why Command pattern for moves?**
   - Natural representation of chess moves
   - Built-in undo support
   - Move history for notation

4. **How to validate complex moves?**
   - First check basic piece movement
   - Then verify path is clear (except Knight)
   - Finally check if move leaves king in check

5. **State pattern for game state?**
   - Clean state transitions
   - Different behavior per state
   - Easy to add new states (draw offers, etc.)
