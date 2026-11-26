# 🏆 Coach Answer: Coding Sliding Window Pack

> **Type:** Coding Pattern Drill  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## Phase 1 — Problem Framing

Strong candidates first decide whether sliding window is valid.

1. Confirm the answer is based on a contiguous range.
2. State whether the window is fixed-size or variable-size.
3. Define the maintained state: sum, frequency map, distinct count, matched count, or deque.
4. Identify the validity predicate and when the answer is recorded.
5. Call out constraints that can break the template, especially negative numbers in sum-window problems.

---

## Phase 2 — Canonical Templates

### Template A: Fixed-Size Rolling State

Used for: maximum sum/average of size `k`, fixed-length frequency matching.

```text
build first window
for each right after first window:
    add entering item
    remove item that is now left of window
    record answer for the full window
```

### Template B: Longest Valid Variable Window

Used for: no repeats, at most K distinct, replacement-style constraints.

```text
for right in [0..n):
    add input[right] to state
    while window is invalid:
        remove input[left] from state
        left += 1
    record maximum valid length
```

### Template C: Minimum Valid Variable Window

Used for: minimum size subarray sum with positive integers, minimum cover variants.

```text
for right in [0..n):
    add input[right] to state
    while window is valid:
        record current length
        remove input[left] from state
        left += 1
```

### Template D: Counting With At-Most Helper

Used for: exactly K distinct values.

```text
exactlyK = atMost(K) - atMost(K - 1)
```

Inside `atMost(K)`, after restoring validity, add `right - left + 1` because every start from `left` to `right` forms a valid subarray ending at `right`.

### Template E: Monotonic Deque Window

Used for: max/min inside each moving window.

```text
remove expired front indices
remove dominated back indices
append current index
front is current best when full window exists
```

---

## Phase 3 — Problem-by-Problem Walkthrough

1. **Maximum Sum Subarray of Size K**
   - Invariant: `window_sum` equals exactly the last `k` elements.
   - Target: `O(n)` time, `O(1)` space.

2. **Minimum Size Subarray Sum**
   - Invariant: positive values make sum monotonic under expansion and contraction.
   - Risk area: negative values require a different technique.
   - Target: `O(n)` time, `O(1)` space.

3. **Longest Substring Without Repeating Characters**
   - Invariant: every active character count is at most one.
   - Target: `O(n)` time, `O(alphabet)` space.

4. **Longest Substring With At Most K Distinct**
   - Invariant: frequency map exactly represents `[left, right]`, and key count is at most `k`.
   - Target: `O(n)` time, `O(min(k, alphabet))` space.

5. **Subarrays With Exactly K Distinct**
   - Reduction: exactly K equals at most K minus at most K minus one.
   - Counting insight: `right - left + 1` valid starts per right endpoint.
   - Target: two linear passes.

6. **Permutation in String**
   - Invariant: fixed window length equals `len(s1)` and counts match target.
   - Target: `O(len(s1) + len(s2))`.

7. **Sliding Window Maximum**
   - Invariant: deque indices are in-window and values decrease front to back.
   - Target: `O(n)` time, `O(k)` space.

8. **Pattern Overview**
   - Interview value is validity-predicate clarity, state maintenance, and complexity proof.

---

## Phase 4 — Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Pattern selection | 20% | Confirms contiguity and identifies fixed/variable/deque template |
| Invariant clarity | 25% | Defines boundaries, state, and validity predicate |
| State maintenance | 25% | Correct add/remove updates for sums, maps, counts, or deque |
| Complexity & edge cases | 20% | Proves linear movement and states realistic space cost |
| Communication | 10% | Explains when the template fails and how it maps to production windows |

---

## Phase 5 — Common Pitfalls

1. Using sliding window for non-contiguous subsequence problems.
2. Applying positive-sum shrink logic when negative values are allowed.
3. Updating answers before validity is restored.
4. Forgetting to remove zero-count keys from frequency maps.
5. Recomputing max/min for every window instead of using a monotonic deque.
6. Claiming all windows are `O(1)` space without bounding alphabet or active distinct keys.

---

## Follow-Up Drill Set

1. Minimum window substring.
2. Longest repeating character replacement.
3. Find all anagram start indices.
4. Shortest subarray with sum at least K when negatives exist.
5. Sliding-window rate limiter with exact log vs bucketed counter trade-offs.

---

## Cross-links

- [Sliding Window Pattern Pack](../05-coding-problems/sliding-window/README.md)
- [Sliding Window Quiz](../quizzes/sliding-window-quiz.md)
- [Sliding Window Flashcards](../flashcards/sliding-window.md)
- [HLD Rate Limiting](../03-hld-concepts/rate-limiting/THEORY.md)
