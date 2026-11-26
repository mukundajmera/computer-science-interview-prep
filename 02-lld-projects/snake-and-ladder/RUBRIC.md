# Snake and Ladder - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies player count, board size, dice rules, exact-roll behavior, extra turns, and undo/replay scope |
| Board modeling | 20% | Represents snakes and ladders as validated position mappings with configurable board size |
| Turn and movement correctness | 30% | Applies dice movement, overflow rule, snake/ladder effects, win detection, and next-player rotation consistently |
| Rule extensibility | 20% | Isolates dice strategy, board setup, move history, and configurable rules without making v1 complex |
| Testing and communication | 15% | Explains v1 to v3 progression and covers edge cases such as no players, invalid board links, and final-square rolls |

## Performance bands
- `1/5`: hard-coded script that moves players but cannot validate board rules or turn order.
- `3/5`: working multi-player game with snakes, ladders, and win detection, but limited configurability or replay support.
- `5/5`: compact game engine with validated board setup, deterministic move records, rule strategies, and clear undo/replay tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
