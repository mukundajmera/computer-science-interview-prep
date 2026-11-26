# Design Approach for Snake and Ladder

A step-by-step thought process for designing the Snake and Ladder game.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Game | ✅ Yes | Main controller |
| Board | ✅ Yes | Game board with snakes/ladders |
| Player | ✅ Yes | Game participant |
| Dice | ✅ Yes | Random number generator |
| Snake | ✅ Yes | Special board element |
| Ladder | ✅ Yes | Special board element |
| Move | ✅ Yes | Recorded action |
| Square | ❌ No | Implicit in position |

**Final Entities**: Game, Board, Player, Dice, Snake, Ladder, Move

---

## Step 2: Define Relationships

```
Game (1) ──uses──> (1) Board
Game (1) ──has──> (n) Player
Game (1) ──uses──> (1) Dice
Board (1) ──contains──> (n) Snake
Board (1) ──contains──> (n) Ladder
Game (1) ──records──> (n) Move
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| Game → Board | Composition | Board is part of game |
| Game → Player | Aggregation | Players can exist independently |
| Board → Snake | Composition | Snakes belong to board |
| Board → Ladder | Composition | Ladders belong to board |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Different dice roll strategies |
| **Factory** | ✅ Yes | Create boards with configurations |
| **Command** | ✅ Yes | Move tracking for undo |
| **Observer** | 🔄 v2 | Notify UI of position changes |
| **Singleton** | ❌ No | Multiple games should be possible |

### Pattern Application:

1. **Strategy Pattern** - DiceStrategy
   - SingleDice, DoubleDice, WeightedDice
   - Easy to add new dice types

2. **Factory Pattern** - BoardFactory
   - Create standard, custom, or random boards
   - Encapsulates board setup complexity

3. **Command Pattern** - MoveCommand
   - Record each move
   - Enable undo functionality

---

## Step 4: Design Classes

### Core Classes:

#### Game
- **Attributes**: 
  - `board: Board`
  - `players: List<Player>`
  - `dice: Dice`
  - `currentPlayerIndex: int`
  - `gameStatus: GameStatus`
  - `moveHistory: List<Move>`
- **Methods**:
  - `addPlayer(name): Player`
  - `rollDice(): int`
  - `playTurn(): Move`
  - `isGameOver(): boolean`
  - `getWinner(): Player`

#### Board
- **Attributes**:
  - `size: int`
  - `snakes: Map<Integer, Integer>`
  - `ladders: Map<Integer, Integer>`
- **Methods**:
  - `getNextPosition(position, roll): int`
  - `hasSnakeAt(position): boolean`
  - `hasLadderAt(position): boolean`
  - `isValidPosition(position): boolean`

#### Player
- **Attributes**:
  - `id: String`
  - `name: String`
  - `position: int`
- **Methods**:
  - `moveTo(position): void`
  - `getPosition(): int`

#### Dice
- **Attributes**:
  - `minValue: int`
  - `maxValue: int`
- **Methods**:
  - `roll(): int`

#### Snake / Ladder
- **Attributes**:
  - `start: int`
  - `end: int`
- **Methods**:
  - `getStart(): int`
  - `getEnd(): int`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Invalid player names
- Duplicate player names
- Invalid board configuration
- Snake/ladder overlaps

### Business Logic:
- Roll exceeds final position (bounce back or stay)
- No players in game
- Player already at final position
- Empty snakes/ladders map
- Single player game

### Game Rules:
- Extra turn on rolling 6
- Three 6s in a row sends player back

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Check snake/ladder | O(n) | O(1) with HashMap |
| Find player position | O(n) | O(1) direct access |
| Move history | List | LinkedList for undo |

### Caching:
- Pre-compute final positions with snakes/ladders
- Cache board validation results

---

## Step 7: Version Progression

### v1-basic
- Standard 100-square board
- Basic dice (1-6)
- Multiple players
- Simple win condition (reach 100)

### v2-extended
- Custom board sizes
- Multiple dice types
- Move history
- Restart functionality
- Custom snakes/ladders

### v3-optimized
- Configurable rules
- Undo moves
- Save/load game
- Tournament mode

---

## Code Organization

```
snake-and-ladder/
├── java/
│   ├── v1-basic/
│   │   ├── Game.java
│   │   ├── Board.java
│   │   ├── Player.java
│   │   ├── Dice.java
│   │   └── SnakeAndLadderDemo.java
│   ├── v2-extended/
│   │   ├── [All v1 classes enhanced]
│   │   ├── Move.java
│   │   ├── BoardFactory.java
│   │   └── DiceStrategy.java
│   └── v3-optimized/
│       └── [Extended with undo/rules]
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why HashMap for snakes/ladders?**
   - O(1) lookup vs O(n) with list
   - Direct position mapping

2. **How to ensure fair dice?**
   - Use SecureRandom for truly random
   - Seed properly

3. **Extensibility for new rules?**
   - Strategy pattern for dice
   - Rule engine for game variations
