# Greedy Overview

## Overview

Greedy is the pattern for problems where one locally optimal choice can be proven safe before solving the rest of the input.

## Mental model

Greedy algorithms commit to a choice before seeing every possible future. That is only safe when the choice preserves an invariant that an optimal solution can also satisfy.

In an interview, the implementation is often short. The proof is the actual answer.

## Requirements and constraints

- Identify the objective before choosing a rule: maximize count, minimize removals, prove reachability, or close a boundary.
- State the local choice and the invariant it preserves.
- Give a counterexample for the tempting wrong heuristic.
- Sort only when the proof depends on order; otherwise prefer a one-pass boundary or balance scan.
- Report complexity from the sort plus scan, usually `O(n log n)` or `O(n)`.

## High-level design / approach

1. Convert the prompt into a safe boundary: earliest finish, farthest reach, prefix balance, last occurrence, minimum price, or endpoint coverage.
2. Prove the boundary with exchange, stays-ahead, boundary, or dominance reasoning.
3. Scan once after preprocessing.
4. Update only the state needed for the invariant.
5. Return the objective, not the intermediate choices unless the prompt asks for them.

## Dry run

For interval selection, sorting by end time turns `[1,4], [2,3], [3,5]` into `[2,3], [1,4], [3,5]`.

Take `[2,3]` because it ends first. Skipping `[1,4]` is safe because it conflicts and leaves less future room. Take `[3,5]` because it starts at the current boundary. The invariant is that the chosen set is compatible and leaves at least as much remaining room as any same-size alternative.

## Language-neutral pseudocode

```text
prepare input order or boundary data
state = initial greedy boundary
for item in input:
    if item satisfies the invariant boundary:
        take or close the greedy choice
        update state
    else:
        skip or reset the candidate
return answer derived from state
```

## Complexity

- Sorted interval problems: `O(n log n)` time, usually `O(1)` extra space beyond output.
- Reachability, balance, partition, and min-price scans: `O(n)` time.
- Space is constant unless the problem needs an auxiliary map such as last occurrence by character.

## Greedy proof checklist

Before coding, say:

1. What is the local choice?
2. What objective does that local choice optimize?
3. Why can an optimal solution be transformed to include that choice?
4. What state remains after the choice?
5. What impossible case must be reported?

If step 3 is weak, pause and test a counterexample.

## Common proof shapes

| Proof shape | Use when | Candidate sentence |
|---|---|---|
| Exchange argument | choosing one interval/item over another | "If an optimal solution chooses a later-ending interval first, I can swap in the earlier-ending interval and not reduce the number of future intervals." |
| Stays-ahead | tracking farthest reach or best prefix | "After scanning each index, my farthest reach is at least as far as any solution using the same number of jumps." |
| Boundary argument | closing segments or resetting starts | "Once this prefix has negative balance, no start inside it can succeed because it inherits an even worse balance." |
| Dominance | one candidate is never worse than another | "A lower buy price before the same sell day dominates every higher buy price." |

## Greedy vs DP

Use DP when choices interact in a way that cannot be summarized by one safe boundary. Use greedy when one candidate dominates alternatives under the objective.

| Prompt shape | Likely pattern | Why |
|---|---|---|
| "fewest coins for arbitrary denominations" | DP | largest coin can block optimal combination |
| "maximum non-overlapping intervals" | greedy | earliest finish leaves most remaining room |
| "0/1 knapsack" | DP | local value/weight ratio can fail |
| "can reach the end" | greedy | only farthest reachable boundary matters |

## System-design transfer

Greedy thinking appears in production when exact global optimization is too expensive:

- cache eviction chooses a local victim;
- load balancers pick a currently attractive target;
- schedulers pick jobs by deadline, priority, or slack;
- delivery systems pick fallback providers in order;
- pricing or alerting systems choose thresholds from recent signals.

For exact algorithms, give a proof. For production heuristics, give metrics and rollback.

## Interview-ready wrap-up

"My greedy choice is safe because it preserves the only future-relevant boundary. I am not just choosing locally; I am proving that any optimal answer can be adjusted to make the same first choice. After that, the remaining subproblem has the same shape, so a one-pass or sorted scan is enough."

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Recognition | Names the objective and candidate boundary |
| Proof | Uses exchange, stays-ahead, boundary, or dominance reasoning |
| Counterexample | Rejects at least one tempting wrong heuristic |
| Implementation | Keeps state minimal and tied to the invariant |
| Complexity | Separates sort cost, scan cost, and auxiliary storage |

## Common pitfalls

1. Saying "greedy works because it seems optimal" without proof.
2. Sorting by the wrong key, especially start time or duration in interval selection.
3. Using greedy for problems where future choices require a richer state, such as arbitrary coin change or weighted interval scheduling.
4. Forgetting endpoint conventions for interval problems.

## Follow-up questions

1. What is the exchange argument for your local choice?
2. Which counterexample breaks the nearest wrong heuristic?
3. When would this become dynamic programming?
4. How would you return the chosen objects, not just the count?

## Variants and extensions

- Weighted intervals require DP or data structures because simple earliest-finish no longer preserves value.
- Limited-capacity route versions may need prefix sums plus feasibility checks.
- Multi-resource scheduling can become heap, flow, or matching instead of one greedy boundary.

## Cross-links

- [Greedy Pattern Pack](./README.md)
- [Activity Selection](./02-activity-selection.md)
- [Gas Station](./05-gas-station.md)
- [Dynamic Programming](../dynamic-programming/README.md)
