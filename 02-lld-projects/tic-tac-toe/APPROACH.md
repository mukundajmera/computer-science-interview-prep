# Design Approach for Tic-Tac-Toe

## Step 1: Identify Core Entities

From the problem statement, the key nouns/entities are:

1. **Board** - The game grid (N×N cells)
2. **Cell** - Individual position on the board
3. **Player** - Participant in the game (Human or AI)
4. **Mark** - X or O symbol
5. **Move** - A player's action (position + mark)
6. **Game** - Controller managing game flow

## Step 2: Define Relationships

```
Game (1) -----> (1) Board
Game (1) -----> (2) Player
Player (1) -----> (1) Mark
Board (1) -----> (N×N) Cell
Move (n) -----> (1) Player
Move (n) -----> (1) Cell
```

**Relationships:**
- Game has one Board (composition)
- Game has exactly two Players (aggregation)
- Board contains N×N Cells (composition)
- Each Player has a Mark (X or O)
- Game maintains Move history

## Step 3: Choose Design Patterns

### 3.1 Strategy Pattern
**For**: Win detection strategies, AI strategies
**Why**: Different board sizes may need different win detection algorithms; AI can have multiple difficulty levels

### 3.2 State Pattern
**For**: Game state management
**Why**: Game behavior changes based on state (NOT_STARTED, IN_PROGRESS, WON, DRAW)

### 3.3 Command Pattern
**For**: Move execution and undo
**Why**: Encapsulate moves as objects to support undo/redo functionality

### 3.4 Template Method Pattern
**For**: Game flow
**Why**: Common game loop with customizable player move logic

### 3.5 Factory Pattern
**For**: Player creation
**Why**: Create different player types (Human, AI) based on configuration

## Step 4: Design Classes

### 4.1 Mark (Enum)
```
Responsibilities: Define player symbols
Values: X, O, EMPTY
```

### 4.2 GameState (Enum)
```
Responsibilities: Define game states
Values: NOT_STARTED, IN_PROGRESS, X_WON, O_WON, DRAW
```

### 4.3 Position
```
Responsibilities: Represent board coordinates
Attributes:
  - row: int
  - col: int
Methods:
  - isValid(boardSize): boolean
```

### 4.4 Board
```
Responsibilities: Manage game grid
Attributes:
  - size: int
  - cells: Mark[][]
  - emptyCells: int
Methods:
  - placeMark(position, mark): boolean
  - removeMark(position): void
  - getMark(position): Mark
  - isEmpty(position): boolean
  - isFull(): boolean
  - display(): void
  - reset(): void
```

### 4.5 Player (Abstract)
```
Responsibilities: Represent game participant
Attributes:
  - name: String
  - mark: Mark
Methods:
  - getMark(): Mark
  - makeMove(board): Position (abstract)
```

### 4.6 HumanPlayer extends Player
```
Responsibilities: Get move from user input
Methods:
  - makeMove(board): Position (from console/UI)
```

### 4.7 AIPlayer extends Player (v2+)
```
Responsibilities: Calculate optimal move
Attributes:
  - strategy: AIStrategy
Methods:
  - makeMove(board): Position (using strategy)
```

### 4.8 Move
```
Responsibilities: Encapsulate a game move
Attributes:
  - position: Position
  - player: Player
  - timestamp: long
```

### 4.9 WinChecker
```
Responsibilities: Detect win conditions
Methods:
  - checkWin(board, lastMove): boolean
  - checkRow(board, row, mark): boolean
  - checkColumn(board, col, mark): boolean
  - checkDiagonals(board, mark): boolean
```

### 4.10 Game
```
Responsibilities: Orchestrate game flow
Attributes:
  - board: Board
  - players: Player[2]
  - currentPlayerIndex: int
  - state: GameState
  - moveHistory: List<Move>
  - winChecker: WinChecker
Methods:
  - start(): void
  - makeMove(position): boolean
  - undoMove(): boolean (v2+)
  - getCurrentPlayer(): Player
  - getState(): GameState
  - isGameOver(): boolean
  - reset(): void
```

## Step 5: Handle Edge Cases

### 5.1 Input Validation
- Position out of bounds
- Already occupied cell
- Game already over
- Invalid player turn

### 5.2 Game State Validation
- Move attempted before game starts
- Move attempted after game ends
- Undo on empty history

### 5.3 Board Edge Cases
- 1×1 board (instant win)
- Even-sized boards
- Large boards (performance)

### 5.4 AI Edge Cases
- First move optimization
- Corner/center strategies
- No valid moves (draw)

## Step 6: Optimization Opportunities

### 6.1 Win Detection Optimization
**Problem**: Checking entire board is O(N²)
**Solution**: Only check row, column, and diagonals affected by last move → O(N)

### 6.2 AI Optimization (Minimax)
**Problem**: Minimax explores all possibilities → O(b^d)
**Solution**: Alpha-beta pruning → O(b^(d/2)) average case

### 6.3 Board State Hashing
**Problem**: Repeated board states in AI search
**Solution**: Zobrist hashing for transposition tables

### 6.4 Symmetric Position Reduction
**Problem**: Many board states are symmetric
**Solution**: Canonical form reduces search space by up to 8x

### 6.5 Move Ordering
**Problem**: Alpha-beta effectiveness depends on move order
**Solution**: Order by center → corners → edges for better pruning

## Version Progression

### v1-basic
- 3×3 board only
- Two human players
- Basic win/draw detection
- Console display

### v2-extended
- N×N board support
- AI player with minimax
- Move history and undo
- Better UI feedback

### v3-optimized
- Alpha-beta pruning
- Optimized win detection
- Parallel game sessions
- Performance improvements
