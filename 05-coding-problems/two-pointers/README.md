# 🔁 Two Pointers Pattern Pack

A focused coding pattern pack for interview rounds that blend algorithms with system design judgment.

---

## 📖 Overview

Two pointers is a family of linear-scan techniques that maintain two moving indices over an array or string.

Typical forms:
- Opposite-end pointers (`left`, `right`) for sorted or boundary-driven decisions.
- Fast/slow pointers for stable in-place transforms.
- Multi-pointer partitions (for example, 3-way partitioning).

---

## ✅ When to Use

Use two pointers when at least one of these holds:
1. You can eliminate many candidates after one comparison.
2. Pointer movement is monotonic (one-way progress, no backtracking).
3. You need `O(1)` extra memory with in-place updates.
4. Sorted order or boundary maxima/minima enables local decisions.

---

## ⚠️ Common Failure Modes

1. Moving the wrong pointer when comparison fails.
2. Losing duplicate handling rules after sorting.
3. Breaking invariants during in-place swaps.
4. Confusing value-domain constraints with index-domain constraints.

---

## 🧠 Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| Invariant clarity | Clearly states what each region/pointer means at every step |
| Complexity reasoning | Explains why scan is linear and space stays constant |
| Edge-case handling | Empty input, duplicates, all-equal, monotonic arrays |
| Follow-up adaptation | Can pivot to counting, dedupe, or partition variants |

---

## 📚 Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-container-with-most-water.md](./02-container-with-most-water.md)
3. [03-two-sum-sorted-array.md](./03-two-sum-sorted-array.md)
4. [04-three-sum.md](./04-three-sum.md)
5. [05-valid-triangle-number.md](./05-valid-triangle-number.md)
6. [06-move-zeroes.md](./06-move-zeroes.md)
7. [07-sort-colors.md](./07-sort-colors.md)
8. [08-trapping-rain-water.md](./08-trapping-rain-water.md)

---

## 🔗 Cross-links

- [Big-O Notation](../../00-theory/complexity-analysis/big-o-notation.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [LLD Rate Limiter](../../02-lld-projects/rate-limiter/)
- [HLD Read Scaling](../../03-hld-concepts/read-scaling/)
- [HLD Caching](../../03-hld-concepts/caching/)
- [Two Pointers Quiz](../../quizzes/two-pointers-quiz.md)
- [Two Pointers Flashcards](../../flashcards/two-pointers.md)
- [Coach Answer: Coding Two Pointers](../../solutions/coding-two-pointers.md)
