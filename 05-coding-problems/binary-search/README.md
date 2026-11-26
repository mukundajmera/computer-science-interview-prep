# 🔎 Binary Search Pattern Pack

A focused coding pattern pack for sorted data, monotonic predicates, boundary discovery, and interview problems where the hard part is proving which half of the search space can be discarded.

---

## 📖 Overview

Binary search is not just "look in the middle of a sorted array." It is a proof technique: maintain a search space, choose a midpoint, use a monotonic fact to discard one side, and stop with an exact answer or the first boundary where a predicate becomes true.

Typical forms:

- Exact search in a sorted array.
- Lower-bound and upper-bound searches over duplicate values.
- Search in rotated sorted arrays.
- Binary search on the answer when feasibility is monotonic.
- Partition-based search across two sorted collections.

---

## ✅ When to Use

Use binary search when all of these are true:

1. The candidate space is ordered, sorted, or can be treated as an ordered range.
2. A midpoint decision can eliminate one side without losing the answer.
3. The predicate is monotonic, such as `false false false true true`.
4. You can state the invariant that remains true after every boundary move.

Strong recognition cues:

- "sorted array" or "sorted matrix"
- "first/last occurrence"
- "minimum possible maximum"
- "smallest capacity/speed/rate that works"
- "rotated sorted"
- "find a threshold"
- "kth/median across sorted structures"

---

## 🚫 When Not to Use

Avoid binary search when:

1. The input has no ordering and no monotonic predicate.
2. The midpoint decision cannot safely discard a side.
3. The feasibility check is more expensive than the search saves.
4. Duplicates destroy the ordering signal unless you handle them explicitly.
5. The problem asks for all solutions, not a single boundary or optimum.

---

## ⚠️ Common Failure Modes

1. Infinite loops from inconsistent boundary updates.
2. Returning `mid` after a boundary search instead of returning `left`.
3. Mixing inclusive and half-open interval rules.
4. Updating `left = mid` or `right = mid` without proving progress.
5. Overflow-prone midpoint formulas in languages with fixed-width integers.
6. Applying answer-space search without proving feasibility is monotonic.
7. Ignoring duplicates in rotated arrays.
8. Failing to define what "not found" returns.

---

## 🧠 Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| Search-space definition | Defines what values or indices are still possible |
| Predicate clarity | States exactly what is true/false and why it is monotonic |
| Boundary movement | Uses consistent inclusive or half-open rules |
| Return semantics | Explains exact search, first true, insertion point, or no-solution output |
| Edge-case handling | Empty input, one element, duplicates, all-left/all-right decisions |
| Follow-up adaptation | Can pivot from array search to answer-space, rotated, and partition variants |

---

## 📚 Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-classic-binary-search.md](./02-classic-binary-search.md)
3. [03-first-position-lower-bound.md](./03-first-position-lower-bound.md)
4. [04-search-insert-position.md](./04-search-insert-position.md)
5. [05-search-in-rotated-sorted-array.md](./05-search-in-rotated-sorted-array.md)
6. [06-find-minimum-in-rotated-sorted-array.md](./06-find-minimum-in-rotated-sorted-array.md)
7. [07-koko-eating-bananas.md](./07-koko-eating-bananas.md)
8. [08-search-a-2d-matrix.md](./08-search-a-2d-matrix.md)

---

## 🔗 Cross-links

- [Big-O Notation](../../00-theory/complexity-analysis/big-o-notation.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Indexing Strategies](../../00-theory/database-concepts/indexing.md)
- [HLD Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [HLD API Design](../../03-hld-concepts/api-design/THEORY.md)
- [HLD Consistent Hashing](../../03-hld-concepts/consistent-hashing/THEORY.md)
- [Binary Search Quiz](../../quizzes/binary-search-quiz.md)
- [Binary Search Flashcards](../../flashcards/binary-search.md)
- [Coach Answer: Coding Binary Search](../../solutions/coding-binary-search.md)
