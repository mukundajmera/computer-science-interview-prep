# Sliding Window Overview

## Overview

Sliding window is a pattern for scanning contiguous ranges while maintaining enough state to answer questions about the current range. The core skill is not memorizing a loop template; it is defining a window invariant and proving each boundary moves only forward.

## Requirements and constraints

- The candidate answer must be a contiguous range.
- Window state must support adding the new right item.
- If the window can shrink, state must also support removing the old left item.
- Boundary movement must be monotonic for near-linear time.
- For variable-length windows, the validity predicate must tell you when to shrink.

## High-level design / approach

1. Choose boundary convention: inclusive `[left, right]` or half-open `[left, right)`.
2. Define maintained state: sum, count map, distinct count, matched count, deque, or timestamp queue.
3. Expand the right boundary and update state.
4. While the window violates the predicate, remove `left` and advance it.
5. Record the answer only at the correct time:
   - after every fixed-size window is formed;
   - after restoring validity for longest valid windows;
   - while validity holds for minimum valid windows;
   - through an `atMost(K)` helper for many counting problems.

## Template selection

| Problem signal | Template |
|---|---|
| exactly `k` elements | fixed-size rolling state |
| longest valid substring/subarray | expand right, shrink while invalid, record max |
| minimum valid substring/subarray | expand right, shrink while valid, record min |
| at most `K` distinct | frequency map + distinct count |
| exactly `K` distinct | `atMost(K) - atMost(K - 1)` |
| permutation/anagram match | frequency deficit or matched-count window |
| max/min in each window | monotonic deque |

## Scoring rubric

| Dimension | What interviewers look for |
|---|---|
| Invariant statement | Clear meaning of boundaries and maintained state |
| Validity predicate | Precise condition for shrink/record decisions |
| Correct timing | Answer is recorded before or after shrink at the right point |
| Complexity defense | Each item enters and leaves the window at most once |
| Constraint awareness | Handles negatives, alphabet size, empty windows, and `k` edge cases |

## Common pitfalls

1. Using sliding window on non-contiguous subsequence problems.
2. Forgetting that negative numbers can break sum-based monotonicity.
3. Confusing `right - left + 1` with `right - left`.
4. Leaving zero-count keys in the frequency map and inflating distinct count.
5. Recomputing window maximum in `O(k)` per step.

## Follow-up questions

1. Why does each pointer move at most `n` times?
2. Which sliding-window problems fail when numbers can be negative?
3. When does a deque become necessary instead of a scalar or map?
4. How does a time-based production sliding window differ from an array index window?

## Variants and extensions

- Sliding log and sliding counter rate limiters.
- Event-time windows with late-arriving records.
- Rolling stream aggregates with bounded retention.
- Approximate windows using buckets or sketches.

## Cross-links

- [Sliding Window Pattern Pack](./README.md)
- [Maximum Sum Subarray of Size K](./02-maximum-sum-subarray-size-k.md)
- [Minimum Size Subarray Sum](./03-minimum-size-subarray-sum.md)
- [Sliding Window Maximum](./08-sliding-window-maximum.md)
- [HLD Rate Limiting](../../03-hld-concepts/rate-limiting/THEORY.md)
