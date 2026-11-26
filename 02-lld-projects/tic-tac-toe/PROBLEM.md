# Tic-Tac-Toe

## Problem Statement

Design and implement a Tic-Tac-Toe game that supports two players taking turns to place their marks (X or O) on a game board. The system should detect wins, draws, and handle game state transitions.

## Functional Requirements

1. **Board Management**
   - Initialize a game board (default 3×3, extensible to N×N)
   - Display the current board state
   - Track empty and occupied cells

2. **Player Management**
   - Support two players with distinct marks (X and O)
   - Alternate turns between players
   - Track whose turn it is

3. **Move Validation**
   - Validate that moves are within board boundaries
   - Prevent moves on already occupied cells
   - Only allow moves when game is in progress

4. **Win Detection**
   - Check for horizontal wins (complete row)
   - Check for vertical wins (complete column)
   - Check for diagonal wins (both diagonals)
   - Announce the winner

5. **Draw Detection**
   - Detect when all cells are filled with no winner
   - Properly end the game as a draw

6. **Game State Management**
   - Track game states: NOT_STARTED, IN_PROGRESS, WON, DRAW
   - Support game reset/restart

7. **Undo Move (v2+)**
   - Allow players to undo their last move
   - Maintain move history

8. **AI Player (v2+)**
   - Implement computer opponent with minimax algorithm
   - Add alpha-beta pruning optimization (v3)

## Non-Functional Requirements

1. **Extensibility**
   - Support N×N boards with N-in-a-row win condition
   - Easy to add new player types (human, AI)

2. **Performance**
   - O(1) move placement
   - O(N) win detection for N×N board
   - Optimized AI with alpha-beta pruning

3. **Thread Safety (v3)**
   - Support concurrent game sessions
   - Thread-safe game state management

## Constraints & Assumptions

- Standard game uses 3×3 board
- X always moves first
- No time limits for moves
- Two players per game (human or AI)

## Sample Interactions

```
Game Started! X moves first.

  1 | 2 | 3
 -----------
  4 | 5 | 6
 -----------
  7 | 8 | 9

Player X, enter position (1-9): 5

  1 | 2 | 3
 -----------
  4 | X | 6
 -----------
  7 | 8 | 9

Player O, enter position (1-9): 1

  O | 2 | 3
 -----------
  4 | X | 6
 -----------
  7 | 8 | 9

Player X, enter position (1-9): 9

  O | 2 | 3
 -----------
  4 | X | 6
 -----------
  7 | 8 | X

Player O, enter position (1-9): 3

  O | 2 | O
 -----------
  4 | X | 6
 -----------
  7 | 8 | X

Player X, enter position (1-9): 1
Invalid move! Cell already occupied.

Player X, enter position (1-9): 2

  O | X | O
 -----------
  4 | X | 6
 -----------
  7 | 8 | X

Player X wins! Three in a column!
```

## Interview Focus Areas

1. **OOP Design**: Clean separation of concerns (Board, Player, Game)
2. **Design Patterns**: Strategy for win detection, Command for undo, State for game states
3. **Algorithm**: Minimax with alpha-beta pruning for AI
4. **Extensibility**: N×N board support, different player types
5. **Testing**: Edge cases, win conditions, draw scenarios
