# Code Walkthrough: Chess Game

## Overview

Complex OOP design with inheritance hierarchy. Tests polymorphism understanding.

---

## File Structure

```
java/v1-basic/
├── Piece.java      # Abstract + all piece types (King, Queen, etc.)
├── Board.java      # 8x8 grid with piece placement
├── Position.java   # Row/Column coordinate
├── Game.java       # Game loop and turn management
└── ChessDemo.java  # Demo entry point
```

```
python/v1-basic/
├── piece.py        # Piece hierarchy
├── board.py        # Board management
├── position.py     # Coordinate class
├── game.py         # Game controller
└── chess_demo.py   # Demo
```

---

## Class Hierarchy

```
            Piece (abstract)
               │
    ┌──────────┼──────────┐
    │          │          │
   King      Queen      Bishop
    │          │          │
   Rook     Knight      Pawn
```

### Piece Interface

```java
abstract class Piece {
    protected Color color;
    protected Position position;
    
    abstract boolean canMove(Position newPos, Board board);
    abstract List<Position> getValidMoves(Board board);
}
```

---

## Move Validation

Each piece implements `canMove()` with specific rules:

| Piece | Movement Rule |
|-------|---------------|
| King | 1 square any direction |
| Queen | Any direction, any distance |
| Rook | Horizontal or vertical |
| Bishop | Diagonal only |
| Knight | L-shape (2+1 or 1+2) |
| Pawn | Forward, capture diagonal |

---

## Interview Questions

### 1. "How do you validate moves?"

```java
boolean isValidMove(Position from, Position to) {
    Piece piece = board.getPiece(from);
    if (piece == null) return false;
    if (!piece.canMove(to, board)) return false;
    if (wouldPutKingInCheck(from, to)) return false;
    return true;
}
```

### 2. "How to detect checkmate?"

```java
boolean isCheckmate(Color color) {
    if (!isInCheck(color)) return false;
    // Try all possible moves
    for (Piece piece : getPieces(color)) {
        for (Position move : piece.getValidMoves()) {
            if (!wouldPutKingInCheck(piece.position, move)) {
                return false; // Has escape move
            }
        }
    }
    return true; // No escape = checkmate
}
```

### 3. "How to implement castling?"

Special move checking in King.canMove():
- King and Rook haven't moved
- No pieces between them
- King doesn't pass through check

### 4. "How would you add en passant?"

Track last move in Game, check in Pawn.canMove():
```java
if (lastMove.isPawnDoubleStep() && canCaptureEnPassant()) { ... }
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Factory** | Create piece by type |
| **Strategy** | Move validation per piece |
| **Observer** | UI updates on board changes |

---

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| isValidMove | O(max moves) | O(1) |
| getValidMoves | O(board size) | O(moves) |
| isCheckmate | O(P × M) | O(M) |

Where P = pieces, M = max moves per piece
