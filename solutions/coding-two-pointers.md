# 🏆 Coach Answer: Coding Two Pointers Pack

> **Type:** Coding Pattern Drill  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## Phase 1 — Problem Framing

Strong candidates begin with pattern selection, not code.

1. Clarify if the input has sorted order or can be sorted safely.
2. Define pointer roles and invariant regions.
3. State elimination logic before implementation.
4. Commit to complexity target.

---

## Phase 2 — Canonical Templates

### Template A: Opposite-End Elimination
Used for: two-sum-sorted, container-with-water, trapping-rain-water (with boundary state).

```text
left = 0, right = n - 1
while left < right:
    evaluate(nums[left], nums[right])
    move exactly one side (or both only on match + dedupe)
```

### Template B: Fast/Slow Compaction
Used for: move-zeroes, remove-element style transforms.

```text
write = 0
for scan in [0..n):
    if keep(nums[scan]):
        swap(nums[write], nums[scan])
        write += 1
```

### Template C: Three-Region Partition
Used for: sort-colors.

```text
left = 0, i = 0, right = n - 1
while i <= right:
    route nums[i] into 0/1/2 region
```

### Template D: Anchor + Two-Pointer Sweep
Used for: 3-sum, triangle counting.

```text
sort(nums)
for anchor in range(...):
    left, right = anchor+1, n-1
    sweep with dedupe or batch counting
```

---

## Phase 3 — Problem-by-Problem Walkthrough

1. **Two Sum (Sorted)**
   - Invariant: all excluded pairs are provably non-matching by sorted monotonicity.
   - Target: `O(n)` / `O(1)`.

2. **Container With Most Water**
   - Invariant: moving taller boundary cannot improve min-height limiter.
   - Target: `O(n)` / `O(1)`.

3. **3-Sum**
   - Reduction: anchor + two-sum-sorted on suffix.
   - Risk area: duplicate control on anchor and side pointers.
   - Target: `O(n^2)` / `O(1)` auxiliary.

4. **Valid Triangle Number**
   - Reduction after sort: check only `a+b>c`.
   - Counting jump: add `right-left` when valid.
   - Target: `O(n^2)` / `O(1)`.

5. **Move Zeroes**
   - Invariant: prefix `[0, write)` is stable non-zero segment.
   - Target: `O(n)` / `O(1)`.

6. **Sort Colors**
   - Invariant: `[0,left)` are 0s, `[left,i)` are 1s, `(right,n-1]` are 2s.
   - Target: `O(n)` / `O(1)`.

7. **Trapping Rain Water**
   - Invariant: smaller side is currently resolvable with its running max.
   - Target: `O(n)` / `O(1)`.

8. **Pattern Overview**
   - Interview value is invariant articulation and adaptation speed.

---

## Phase 4 — Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Pattern selection | 20% | Picks correct pointer template quickly |
| Invariant clarity | 25% | Explains regions/roles unambiguously |
| Correct movement logic | 25% | Pointer updates are defensible and minimal |
| Complexity & edge cases | 20% | Accurate asymptotics + robust edge handling |
| Communication | 10% | Narrates decisions and trade-offs clearly |

---

## Phase 5 — Common Pitfalls

1. “Looks right” explanation without invariant proof.
2. Wrong pointer movement direction in elimination problems.
3. Incomplete duplicate handling in 3-sum.
4. Incrementing scan pointer too early in sort-colors.
5. Misordered `max` updates in trapping rain water.

---

## Follow-Up Drill Set

1. 3-sum closest.
2. Count unique pairs with target in sorted array.
3. Return all max-area index pairs for container problem.
4. Stable partition by custom predicate.
5. Streaming adaptation with bounded memory.

---

## Cross-links

- [Two Pointers Pattern Pack](../05-coding-problems/two-pointers/README.md)
- [Two Pointers Quiz](../quizzes/two-pointers-quiz.md)
- [Two Pointers Flashcards](../flashcards/two-pointers.md)
