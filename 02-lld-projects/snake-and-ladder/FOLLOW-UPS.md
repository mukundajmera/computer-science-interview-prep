# Snake and Ladder - Follow-Up Questions

## Follow-up questions
1. How would you support exact-roll-to-win and bounce-back rules using the same movement flow?
2. How would you add extra turns on rolling six, including a three-sixes penalty?
3. What validation would you run before accepting a custom board configuration?
4. How would you make dice rolls deterministic in tests but random in production play?
5. What data would a `Move` store to support replay, undo, and audit logs?

## Variants and extensions
1. Multiple dice with different ranges or weighted probabilities.
2. Tournament mode across many game instances.
3. Save/load support for unfinished games.
4. Custom square effects beyond snakes and ladders.

## Interviewer probes to prepare
- "When exactly is the winner set?"
- "Where do snakes and ladders apply in the movement pipeline?"
- "Why should dice be separate from `Game.playTurn`?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
