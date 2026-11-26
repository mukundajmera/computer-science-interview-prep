# Tic-Tac-Toe - Follow-Up Questions

## Follow-up questions
1. How would you generalize from 3x3 to N x N with a configurable K-in-a-row win condition?
2. How would you implement undo while preserving game state after a prior win or draw?
3. Where should minimax live so human and AI players share the same move contract?
4. How would alpha-beta pruning and move ordering improve AI performance?
5. How would you run many game sessions concurrently without shared mutable board state?

## Variants and extensions
1. Different AI difficulty levels through strategy selection.
2. Match series with player statistics.
3. Networked two-player game with optimistic UI updates.
4. Larger boards with transposition-table caching for AI search.

## Interviewer probes to prepare
- "What owns turn switching?"
- "What is the fastest win check after one move?"
- "How do you keep undo from creating impossible states?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
