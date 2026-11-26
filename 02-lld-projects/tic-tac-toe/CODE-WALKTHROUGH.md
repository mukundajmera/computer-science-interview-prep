# Code Walkthrough: Tic Tac Toe

## Overview

Simple game for basic OOP. Good for demonstrating MVC pattern.

---

## File Structure

```
java/v1-basic/
├── Board.java      # 3x3 grid with win detection
├── Player.java     # Player entity (human/AI)
├── Game.java       # Game loop controller
├── Move.java       # Move representation
└── TicTacToeDemo.java
```

---

## Win Detection

### Algorithm

```java
// Check rows, columns, diagonals
boolean checkWin(char symbol) {
    // Rows
    for (int i = 0; i < 3; i++) {
        if (board[i][0] == symbol && 
            board[i][1] == symbol && 
            board[i][2] == symbol) return true;
    }
    // Columns
    for (int j = 0; j < 3; j++) {
        if (board[0][j] == symbol && 
            board[1][j] == symbol && 
            board[2][j] == symbol) return true;
    }
    // Diagonals
    if (board[0][0] == symbol && board[1][1] == symbol && board[2][2] == symbol) return true;
    if (board[0][2] == symbol && board[1][1] == symbol && board[2][0] == symbol) return true;
    return false;
}
```

---

## Interview Questions

### 1. "How to extend to NxN board?"

Generalize win condition:
```java
boolean checkWin(int row, int col, int n) {
    // Check if placing at (row,col) creates n-in-a-row
}
```

### 2. "How to add AI opponent?"

Minimax algorithm:
```java
int minimax(Board board, boolean isMax) {
    if (terminal(board)) return evaluate(board);
    if (isMax) return max(minimax for all moves);
    else return min(minimax for all moves);
}
```

### 3. "How to handle multiple games?"

```java
class GameManager {
    Map<String, Game> activeGames;
    Game createGame(Player p1, Player p2);
}
```

---

## Complexity

| Operation | Time |
|-----------|------|
| makeMove | O(1) |
| checkWin | O(N) for NxN |
| Minimax AI | O(b^d) |

---

## 🐍 Python Implementation Notes

The Python implementation favors composition and clean value objects:

### Key Python Patterns

| Java Construct | Python Equivalent | Notes |
|----------------|-------------------|-------|
| `enum` | `enum.Enum` | `Mark(Enum)` for X/O, `GameStatus(Enum)` |
| Value objects | `@dataclass(frozen=True)` | `Position` as immutable value type with `__eq__`/`__hash__` |
| `interface` (WinChecker) | ABC or standalone functions | Win detection as a composable strategy |
| `Optional<Player>` | `Optional[Player]` | Winner tracking |
| Array grid | `List[List[Optional[Mark]]]` | Board state with `None` for empty cells |

### Version Progression (Python)

- **v1-basic**: Core game loop with `Board`, `Player`, `Position`, `WinChecker`, and `GameState`. Uses `@dataclass` for `Position` and `Enum` for marks.
- **v2-extended**: Adds AI player (minimax), undo/redo support, and configurable board sizes.
- **v3-optimized**: O(1) win checking with row/column/diagonal counters, tournament support, and thread-safe game manager.

### Running Python Tests

```bash
cd 02-lld-projects/tic-tac-toe
python -m pytest python/tests/ -v
```

---

## Interview Extension Hooks (v3)

For follow-up variants, review:
- `java/v3-optimized/GameFlowCoordinator.java`
- `python/v3-optimized/game_flow_coordinator.py`

These contracts separate turn policy and win-resolution policy so new rule variants can be added safely.
