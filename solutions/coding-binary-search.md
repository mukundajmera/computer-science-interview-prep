# 🏆 Coach Answer: Coding Binary Search Pack

> **Type:** Coding Pattern Drill  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## Phase 1 — Problem Framing

Strong candidates do not start with `while left < right`. They first prove that binary search is valid.

1. Confirm the data is sorted, globally ordered, or governed by a monotonic predicate.
2. State the search space: indices, values, capacities, partition sizes, or virtual row-major positions.
3. State the contract: exact index, first true, insertion point, minimum feasible answer, or boolean existence.
4. Choose one interval convention and explain what `left` and `right` mean.
5. Call out edge cases: empty input, one element, two elements, duplicates, all-false/all-true predicates, and no-solution behavior.

---

## Phase 2 — Canonical Templates

### Template A: Exact Search

Used for: classic search in sorted array, virtual sorted matrix lookup.

```text
left = 0
right = n - 1
while left <= right:
    mid = left + (right - left) // 2
    if value(mid) == target:
        return found result
    if value(mid) < target:
        left = mid + 1
    else:
        right = mid - 1
return not found
```

Invariant: if the target exists and has not been returned, it remains inside `[left, right]`.

### Template B: Lower Bound / First True

Used for: first occurrence, search insert position, first bad version, first event after cursor.

```text
left = 0
right = n
while left < right:
    mid = left + (right - left) // 2
    if predicate(mid) is true:
        right = mid
    else:
        left = mid + 1
return left
```

Invariant: everything before `left` is known false; `right` and beyond remain possible first-true positions.

### Template C: Rotated Sorted Array

Used for: search in rotated sorted array.

```text
while left <= right:
    mid = ...
    if nums[mid] == target:
        return mid
    if nums[left] <= nums[mid]:
        decide whether target lies in sorted left half
    else:
        decide whether target lies in sorted right half
```

The distinct-value assumption matters. With duplicates, `nums[left] == nums[mid] == nums[right]` may force linear boundary trimming.

### Template D: Minimum in Rotated Sorted Array

Used for: pivot/minimum discovery.

```text
while left < right:
    mid = ...
    if nums[mid] > nums[right]:
        left = mid + 1
    else:
        right = mid
return nums[left]
```

`mid` is retained when it may be the minimum.

### Template E: Binary Search on Answer

Used for: Koko Eating Bananas, shipping capacity, split array largest sum, minimum throughput.

```text
left = minimum_possible_answer
right = maximum_possible_answer
while left < right:
    mid = ...
    if feasible(mid):
        right = mid
    else:
        left = mid + 1
return left
```

Complexity is `O(feasibility_cost * log(answer_range))`.

### Template F: Virtual Index Search

Used for: row-major sorted matrix, sorted block pages, sparse index lookup.

```text
row = mid // cols
col = mid % cols
value = matrix[row][col]
```

This works only when the virtual order is globally sorted.

---

## Phase 3 — Problem-by-Problem Walkthrough

1. **Classic Binary Search**
   - Invariant: target remains in `[left, right]`.
   - Target: `O(log n)` time, `O(1)` space.

2. **First Position / Lower Bound**
   - Invariant: all indices before `left` are too small.
   - Risk area: equality does not mean return immediately when first occurrence is required.

3. **Search Insert Position**
   - Return contract: first index where value is at least target, including `n`.
   - Production analogy: first record after a stable cursor.

4. **Search in Rotated Sorted Array**
   - Invariant: target remains in the active range.
   - Decision: identify the sorted half, then decide whether target belongs there.

5. **Find Minimum in Rotated Sorted Array**
   - Invariant: minimum remains in `[left, right]`.
   - Risk area: do not discard `mid` when it may be the minimum.

6. **Koko Eating Bananas**
   - Search space: speeds from `1` to `max(piles)`.
   - Predicate: total hours at speed `s` is `<= h`.
   - Target: `O(n log max(pile))`.

7. **Search a 2D Matrix**
   - Invariant: target's virtual row-major index remains in range.
   - Risk area: global row-major order is required.

8. **Elite Follow-Up: Median of Two Sorted Arrays**
   - Search space: partition size in the smaller array.
   - Validity: `A_left <= B_right` and `B_left <= A_right`.
   - Target: `O(log min(m, n))`.

---

## Phase 4 — Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Pattern validation | 20% | Confirms sortedness, ordered range, or monotonic predicate |
| Invariant clarity | 25% | Defines active range and what each boundary proves |
| Boundary correctness | 25% | Uses consistent interval rules and avoids skipped candidates |
| Complexity & edge cases | 20% | Separates search iterations from predicate cost and handles duplicates/no-solution |
| Communication | 10% | Narrates why one side is impossible before moving a boundary |

---

## Phase 5 — Common Pitfalls

1. Applying binary search without sortedness or monotonicity.
2. Mixing inclusive and half-open interval rules.
3. Returning `mid` after a boundary search.
4. Discarding `mid` when it may still be the first true answer.
5. Forgetting post-loop validation for first occurrence.
6. Treating rotated-array duplicates as free.
7. Claiming answer-space search is `O(log n)` while each feasibility check scans `n` items.
8. Flattening a matrix instead of mapping virtual indices.

---

## Follow-Up Drill Set

1. Last occurrence and duplicate count with lower/upper bound.
2. First bad version.
3. Capacity to ship packages within D days.
4. Split array largest sum.
5. Kth smallest in a sorted matrix.
6. Median of two sorted arrays.
7. Consistent-hash successor lookup with wraparound.
8. SSTable block lookup from sparse index boundaries.

---

## Cross-links

- [Binary Search Pattern Pack](../05-coding-problems/binary-search/README.md)
- [Binary Search Quiz](../quizzes/binary-search-quiz.md)
- [Binary Search Flashcards](../flashcards/binary-search.md)
- [HLD Search Systems](../03-hld-concepts/search-systems/THEORY.md)
- [HLD Consistent Hashing](../03-hld-concepts/consistent-hashing/THEORY.md)
