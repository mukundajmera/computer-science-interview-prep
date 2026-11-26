# Greedy Pattern Pack

A focused coding pattern pack for problems where a local choice can be proven safe: interval scheduling, reachability, circular feasibility, partition boundaries, one-pass profit, and endpoint minimization.

## Overview

Greedy is not "pick what looks best." It is a proof style.

A greedy solution is interview-ready only when you can say why the local choice cannot hurt the global answer. That proof usually takes one of three shapes:

1. **Exchange argument:** replace part of an optimal answer with the greedy choice without making the answer worse.
2. **Stays-ahead argument:** after each step, the greedy solution is at least as good as any alternative on the metric that matters.
3. **Cut or boundary argument:** once a boundary is fixed, no earlier decision can improve the future.

If you cannot give one of those arguments, call the method a heuristic, not an exact greedy algorithm.

## When to Use

Use greedy when the problem gives you:

1. A sorted order that makes the next safe choice obvious.
2. Intervals where earliest end, latest start, or farthest reach dominates.
3. A resource budget that can be updated with a local invariant.
4. A one-pass boundary such as minimum price so far or farthest reachable index.
5. A partition or coverage goal where closing the current group early is safe.

Strong recognition cues:

- "maximum number of non-overlapping intervals"
- "minimum removals", "minimum arrows"
- "can reach the end"
- "complete a circuit"
- "best profit with one transaction"
- "partition so each item appears in one group"

## When Not to Use

Avoid greedy when:

1. Local best choices can block a better later combination.
2. The prompt asks for all valid outputs.
3. The state depends on multiple previous decisions and needs DP.
4. The proof depends on a property the input does not guarantee.
5. You are optimizing a production policy but cannot tolerate heuristic error.

The classic warning is coin change: choosing the largest coin first is not generally correct unless the denomination system has a proven canonical property.

## Pattern Taxonomy

| Variant | Best fit | Key invariant |
|---|---|---|
| Earliest-finish interval greedy | activity selection, non-overlap | the chosen interval leaves maximum room for the future |
| Farthest-reach greedy | jump game reachability, coverage | farthest boundary represents every reachable position scanned so far |
| Balance/reset greedy | gas station, prefix feasibility | a failed segment cannot contain a valid start |
| Boundary partition greedy | partition labels | close a segment only after all included symbols end |
| Min-so-far scan | one-transaction stock profit | best sell today uses the lowest previous buy |
| Endpoint coverage greedy | arrows, cameras, taps | one chosen endpoint covers as many compatible intervals as possible |
| Heuristic greedy | load assignment, cache policy | policy is monitored because exact optimality is not guaranteed |

## Common Failure Modes

1. Saying "greedy works" without a proof.
2. Sorting by start time when the proof needs end time.
3. Updating a reach boundary from an index that is already unreachable.
4. Treating a local reset as valid without proving the skipped prefix cannot be optimal.
5. Ignoring impossible cases such as unreachable indexes or negative total gas.
6. Confusing interval merge with interval selection.
7. Using greedy for coin change, knapsack, or scheduling variants that need DP.
8. Presenting a production heuristic as exact without metrics, rollback, or guardrails.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| Choice rule | Names the exact local choice and what it optimizes |
| Proof | Uses exchange, stays-ahead, or boundary reasoning |
| Sorting key | Justifies end time, start time, reach, or value ordering |
| Edge cases | Handles empty input, ties, impossibility, and circular resets |
| Complexity | Counts sorting plus one-pass scan |
| Follow-up depth | Can distinguish exact greedy from heuristic production policy |

## 60-90 Second Answer

Say:

"I use greedy only after I identify a safe local choice. For interval selection, sorting by earliest end works because any optimal solution using a later-ending first interval can exchange it for the earliest-ending interval and leave at least as much room for the rest. For reachability, I track the farthest index reachable from all scanned reachable positions, so each scan step preserves the best possible future boundary. I will state the invariant, prove why skipped choices cannot improve the answer, handle impossible cases explicitly, and give complexity as sorting plus linear scan, usually `O(n log n)` or `O(n)` when no sorting is needed."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-activity-selection.md](./02-activity-selection.md)
3. [03-non-overlapping-intervals.md](./03-non-overlapping-intervals.md)
4. [04-jump-game.md](./04-jump-game.md)
5. [05-gas-station.md](./05-gas-station.md)
6. [06-partition-labels.md](./06-partition-labels.md)
7. [07-best-time-to-buy-sell-stock.md](./07-best-time-to-buy-sell-stock.md)
8. [08-minimum-arrows-burst-balloons.md](./08-minimum-arrows-burst-balloons.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Caching](../../03-hld-concepts/caching/THEORY.md)
- [Load Balancing](../../03-hld-concepts/load-balancing/THEORY.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
- [Quick Commerce Delivery HLD](../../04-hld-projects/quick-commerce-delivery/)
- [Greedy Quiz](../../quizzes/greedy-quiz.md)
- [Greedy Flashcards](../../flashcards/greedy.md)
- [Coach Answer: Coding Greedy](../../solutions/coding-greedy.md)
