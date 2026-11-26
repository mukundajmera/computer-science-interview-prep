# Coach Answer: Coding Greedy Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 45 minutes

## Phase 1 - Problem Framing

Strong candidates do not say "greedy means sort." They name the local choice and prove it.

1. Identify the objective: maximize count, minimize removals, decide reachability, or minimize covering points.
2. Identify the local choice: earliest end, farthest reach, lowest buy, reset start, or current segment boundary.
3. State the invariant preserved after every choice.
4. Give a proof shape: exchange, stays-ahead, boundary, or dominance.
5. Name the counterexample family where greedy would fail.
6. State sorting cost separately from scan cost.
7. If this is a production heuristic, add metrics and rollback instead of claiming exact optimality.

## Phase 2 - Canonical Templates

### Template A: Earliest-Finish Interval Selection

```text
sort intervals by end
last_end = -infinity
kept = 0
for interval in intervals:
    if interval.start >= last_end:
        kept += 1
        last_end = interval.end
return kept
```

Use for activity selection and non-overlapping intervals.

### Template B: Farthest-Reach Scan

```text
farthest = 0
for i in range(n):
    if i > farthest:
        return false
    farthest = max(farthest, i + reach[i])
return true
```

Use when the only future-relevant fact is the best boundary reached so far.

### Template C: Balance Reset

```text
start = 0
tank = 0
total = 0
for i in range(n):
    net = gain[i] - cost[i]
    tank += net
    total += net
    if tank < 0:
        start = i + 1
        tank = 0
return start if total >= 0 else -1
```

Use when a failed prefix proves every start inside it is invalid.

### Template D: Boundary Closure

```text
last = map item -> last_position
start = 0
end = 0
for i, item in sequence:
    end = max(end, last[item])
    if i == end:
        emit segment start..end
        start = i + 1
```

Use when a segment cannot close until all included keys end.

### Template E: Min-so-far Scan

Invariant: before evaluating today as a sell day, `min_price` is the lowest valid buy price from earlier days.

```text
min_price = +infinity
best = 0
for price in prices:
    best = max(best, price - min_price)
    min_price = min(min_price, price)
return best
```

Use for one-transaction stock profit and other left-to-right "best prior value" scans.

Failure mode: sorting the values destroys time order and can accidentally allow the action before its prerequisite.

### Template F: Endpoint Coverage

Invariant: all scanned intervals before the current one are covered, and `point` is the latest safe point for the earliest-ending uncovered interval.

```text
sort intervals by end
points = 0
point = none
for interval in intervals:
    if point is none or interval.start > point:
        points += 1
        point = interval.end
return points
```

Use for minimum arrows, minimum cameras on intervals, and point-covering variants.

Failure mode: sorting by start can still be valid only if you shrink the active overlap end; sorting by start and choosing starts blindly overcounts.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Activity Selection**
   - Choice: earliest finishing compatible interval.
   - Proof: exchange a later-finishing first interval with the greedy one.

2. **Non-overlapping Intervals**
   - Objective: minimum removals.
   - Reframe: maximize kept intervals, then remove the rest.

3. **Jump Game**
   - State: farthest reachable index.
   - Failure: scan reaches `i > farthest`.

4. **Gas Station**
   - State: current candidate start and tank balance.
   - Reset: a negative segment invalidates every start inside it.

5. **Partition Labels**
   - State: farthest last occurrence for characters in current segment.
   - Close when current index reaches that boundary.

6. **Best Time to Buy and Sell Stock**
   - State: lowest prior buy price.
   - Dominance: lower buy price is never worse for the same sell day.

7. **Minimum Arrows to Burst Balloons**
   - Choice: shoot at the earliest end of first uncovered interval.
   - Proof: latest point that still covers first interval can only help future coverage.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Local choice | 20% | Names the exact choice and ordering key |
| Proof quality | 30% | Uses exchange, stays-ahead, boundary, or dominance reasoning |
| Counterexamples | 15% | Rejects greedy when future-dependent choices break safety |
| Edge cases | 15% | Handles ties, impossible cases, empty inputs, and endpoint conventions |
| Complexity | 10% | Separates sort cost from scan cost |
| Communication | 10% | Explains exact algorithm vs production heuristic clearly |

## Phase 5 - Common Pitfalls

1. Sorting by start time in an earliest-finish problem.
2. Calling every short solution greedy.
3. Forgetting total feasibility in Gas Station.
4. Updating Jump Game reach from unreachable indexes.
5. Closing Partition Labels before all characters end.
6. Sorting stock prices and losing time order.
7. Using `>=` instead of `>` for inclusive interval coverage.
8. Claiming production heuristics are exact without proof.

## System Design Transfer Script

| Greedy concept | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Earliest finish | deadline-aware job scheduling | starvation, priority inversion, burst overload | missed-deadline rate, queue age, retry rate |
| Farthest reach | fallback or rollout layer reachability | hidden unreachable segment | coverage audit, failure-domain drill |
| Balance reset | route/provider budget feasibility | repeated failed prefixes | deficit counters, fallback success rate |
| Boundary closure | tenant-safe batch segmentation | key crossing batches | batch-isolation violations |
| Local heuristic | cache eviction or load assignment | skew, hot keys, unfairness | p95 latency, eviction miss rate, shard skew |

## Follow-Up Drill Set

1. Meeting Rooms II.
2. Jump Game II.
3. Best Time to Buy and Sell Stock II.
4. Candy.
5. Queue Reconstruction by Height.
6. Reorganize String.
7. Minimum Number of Refueling Stops.
8. Huffman Coding / Minimum Merge Cost.

## Cross-links

- [Greedy Pattern Pack](../05-coding-problems/greedy/README.md)
- [Greedy Quiz](../quizzes/greedy-quiz.md)
- [Greedy Flashcards](../flashcards/greedy.md)
- [Job Scheduler HLD](../04-hld-projects/job-scheduler/)
- [Quick Commerce Delivery HLD](../04-hld-projects/quick-commerce-delivery/)
