# Connect Four — Common Interview Pitfalls

## 1) Mixing orchestration and board logic
Keep turn/state transitions in `Game`; keep grid mechanics in `Board`.

## 2) Full-board rescans after every move
Win checks should evaluate lines from the last placed disc.

## 3) Missing invalid turn validation
Reject moves from non-current player explicitly.

## 4) Silent mutations after game over
Reject moves after `WON`/`DRAW` to preserve deterministic behavior.

## 5) Unstable bot behavior
Use deterministic tie-breakers to keep tests reproducible.
