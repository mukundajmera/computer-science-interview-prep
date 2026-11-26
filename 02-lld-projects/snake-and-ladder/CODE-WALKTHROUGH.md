# Code Walkthrough: Snake and Ladder

## Overview

Classic board game - tests random events and state machine concepts.

---

## File Structure

```
java/v1-basic/
├── Board.java       # Game board with snakes/ladders
├── Player.java      # Player entity
├── Snake.java       # Snake entity (move down)
├── Ladder.java      # Ladder entity (move up)
├── Dice.java        # Random dice roll
└── SnakeLadderDemo.java
```

---

## Core Logic

### Board Setup

```java
class Board {
    int size = 100;
    Map<Integer, Integer> snakes;   // head -> tail
    Map<Integer, Integer> ladders;  // bottom -> top
    
    int getDestination(int position) {
        if (snakes.containsKey(position)) 
            return snakes.get(position);
        if (ladders.containsKey(position)) 
            return ladders.get(position);
        return position;
    }
}
```

### Game Loop

```
1. Roll dice
2. Calculate new position
3. Check snake/ladder at new position
4. Apply snake/ladder effect
5. Check if won (position == 100)
6. Next player's turn
```

---

## Interview Questions

### 1. "How to prevent infinite loops?"

Validate board setup:
```java
boolean isValidBoard() {
    // No circular snake-ladder chains
    // No snake at 100
    // No ladder at 1
}
```

### 2. "How to add multiple dice?"

```java
class Dice {
    int count;
    int rollAll() {
        return IntStream.range(0, count)
            .map(i -> random.nextInt(6) + 1)
            .sum();
    }
}
```

### 3. "How to save/load game state?"

Memento pattern:
```java
class GameState {
    Map<Player, Integer> positions;
    Player currentTurn;
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Strategy** | Different board layouts |
| **Observer** | UI updates on moves |
| **Memento** | Save/restore game |
