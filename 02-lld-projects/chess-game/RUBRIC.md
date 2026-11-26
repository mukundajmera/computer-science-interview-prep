# Chess Game — Interview Scoring Rubric

Use this rubric to score solution quality consistently across design depth, correctness, and communication.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Interview Timeline (45 Minutes)

- **00:00 - 05:00**: Requirements gathering and scope alignment. Deciding what rules to include (en passant, etc.).
- **05:00 - 10:00**: Core domain modeling (Board, Piece, Move, Player) and class design.
- **10:00 - 30:00**: Detailed LLD implementation. Implementing piece movement and move validation.
- **30:00 - 40:00**: Addressing complex rules (checkmate, castling) and state management.
- **40:00 - 45:00**: Follow-up questions, optimizations (undo, AI), and Q&A.

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Distinguishes core game rules, scopes out AI vs 2-player early. |
| Domain modeling | 20% | Clean OO design: abstract Piece, distinct Board, GameController. |
| Behavioral correctness | 25% | Handles pin, check detection, and special moves logically without massive bugs. |
| Extensibility and variants | 20% | Command pattern for moves (Undo), Strategy pattern for piece movement. |
| Code and communication quality | 15% | Clear APIs, articulate narrative, DRY code principles applied. |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: Starts coding immediately without scoping rules.
- **3**: Captures basic movement but forgets edge cases like promotion.
- **5**: Explicitly scopes the problem, acknowledges complex rules early to guide design.

### 2. Domain modeling
- **1**: One giant `Game` class with switch statements for piece types.
- **3**: Core entities exist, but Board handles too much business logic.
- **5**: Strong SRP. Uses polymorphism for piece movement. Separation of UI and logic.

### 3. Behavioral correctness
- **1**: Fails basic move validation or ignores check scenarios entirely.
- **3**: Mostly correct flow, but struggles with complex scenarios like discovering a check.
- **5**: Robust validation, clean check/checkmate detection strategy.

### 4. Extensibility and variants
- **1**: Rigid structure; impossible to implement an "Undo" feature without rewriting.
- **3**: Mentions patterns conceptually but fails to provide structural hooks in code.
- **5**: Concrete hooks for variants. Implements Command pattern naturally for move history.

### 5. Code and communication quality
- **1**: Confusing narrative, long mixed methods, poorly named variables.
- **3**: Understandable design with moderate justification.
- **5**: Crisp explanation, focused APIs, clean and readable code.

---

## Hard Gates (Failing Any Gate Caps Score)

1. Fails to use polymorphism or inheritance for Piece movement logic.
2. Mixing UI/Console rendering logic inside core game engine classes.
3. No valid mechanism proposed for detecting "Check" or "Checkmate".
4. Hardcoding logic that permanently prevents implementing an Undo feature.
