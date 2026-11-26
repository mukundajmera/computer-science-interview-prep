# 🔎 Binary Search Flashcards

> **40 question-only flashcards for binary-search pattern mastery**

---

## Foundations (10 Cards)

### Card 1
**Front:** What makes a problem a binary-search candidate?

---

### Card 2
**Front:** What is the difference between sorted data and a monotonic predicate?

---

### Card 3
**Front:** What does a binary-search invariant need to state?

---

### Card 4
**Front:** Why must each midpoint decision discard at least one candidate?

---

### Card 5
**Front:** What is the safest midpoint formula in fixed-width integer languages?

---

### Card 6
**Front:** What is the difference between exact search and boundary search?

---

### Card 7
**Front:** When should binary search return `-1`?

---

### Card 8
**Front:** What does lower bound return?

---

### Card 9
**Front:** What does upper bound return?

---

### Card 10
**Front:** Give one strong anti-signal for using binary search.

---

## Boundary Mechanics (10 Cards)

### Card 11
**Front:** When is `left <= right` usually the right loop guard?

---

### Card 12
**Front:** When is `left < right` usually the right loop guard?

---

### Card 13
**Front:** Why can `left = mid` cause an infinite loop?

---

### Card 14
**Front:** Why does lower-bound search keep `mid` when the predicate is true?

---

### Card 15
**Front:** At loop end, what does `left` represent in a lower-bound search?

---

### Card 16
**Front:** Why should first-occurrence search validate the value after the loop?

---

### Card 17
**Front:** What are the edge cases for search insert position?

---

### Card 18
**Front:** How do duplicates change exact-search requirements?

---

### Card 19
**Front:** What is the complexity proof for classic binary search?

---

### Card 20
**Front:** What should you say before choosing inclusive vs half-open intervals?

---

## Variants and Advanced Searches (10 Cards)

### Card 21
**Front:** In a rotated sorted array with distinct values, what does each midpoint reveal?

---

### Card 22
**Front:** How do you decide whether the left half is sorted in rotated-array search?

---

### Card 23
**Front:** Why can duplicates degrade rotated-array search?

---

### Card 24
**Front:** In find-minimum-in-rotated-array, why compare `nums[mid]` with `nums[right]`?

---

### Card 25
**Front:** What makes binary search on answer valid?

---

### Card 26
**Front:** What is the complexity form for answer-space search with an `O(n)` feasibility check?

---

### Card 27
**Front:** In Koko Eating Bananas, what is the searched value range?

---

### Card 28
**Front:** Why should `can(mid)` keep `mid` when searching for a minimum feasible answer?

---

### Card 29
**Front:** How do you map a virtual 1D matrix index to `(row, col)`?

---

### Card 30
**Front:** Why is median of two sorted arrays a partition search rather than direct value search?

---

## System Design Transfer (10 Cards)

### Card 31
**Front:** How does lower bound show up in consistent-hash ring lookup?

---

### Card 32
**Front:** How does binary search relate to database index seek?

---

### Card 33
**Front:** How does an SSTable sparse index use binary-search reasoning?

---

### Card 34
**Front:** How does keyset pagination resemble lower-bound search?

---

### Card 35
**Front:** How can binary search support capacity planning?

---

### Card 36
**Front:** Why does predicate cost matter in production answer-space search?

---

### Card 37
**Front:** What should you monitor when binary-searching operational thresholds?

---

### Card 38
**Front:** What breaks if a sorted index is stale or not the source of truth?

---

### Card 39
**Front:** How can binary search reduce reads across sorted shard pages?

---

### Card 40
**Front:** Give a concise interview wrap-up template for any binary-search problem.
