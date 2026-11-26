# Snake and Ladder - Common Pitfalls

## Common pitfalls
1. Hard-coding a 100-square board and single die after the requirements call out configurability.
2. Applying snakes and ladders before handling the exact-roll or overflow rule.
3. Allowing invalid board links such as snake tails above heads, ladder tops below bottoms, or overlapping starts.
4. Advancing the turn before recording the full move result for replay or undo.
5. Mixing random dice generation with game logic so tests cannot control rolls.

## Why these fail interviews
- They make common rule variations expensive to add.
- They create off-by-one and final-square bugs that are easy for interviewers to probe.
- They prevent deterministic tests for a game whose core behavior depends on random rolls.

## Mitigations
- Validate board configuration at setup and store jumps in O(1) maps by start position.
- Define the overflow rule before coding movement.
- Record each move with player, roll, start, intermediate, final, and snake/ladder effect.
- Inject dice behavior so tests can use fixed rolls.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
