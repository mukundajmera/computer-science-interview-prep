# 🪟 Sliding Window Flashcards

> **40 question-only flashcards for sliding-window pattern mastery**

---

## Foundations (10 Cards)

### Card 1
**Front:** What makes a problem a sliding-window candidate?

---

### Card 2
**Front:** What is the difference between fixed-size and variable-size windows?

---

### Card 3
**Front:** What does the window invariant need to state?

---

### Card 4
**Front:** Why must window boundaries move monotonically?

---

### Card 5
**Front:** What is a validity predicate in sliding-window problems?

---

### Card 6
**Front:** When do negative numbers break the basic sum-window template?

---

### Card 7
**Front:** What is the safest way to explain sliding-window time complexity?

---

### Card 8
**Front:** Why is `O(1)` space not always true for sliding windows?

---

### Card 9
**Front:** What is the inclusive window length formula for `[left, right]`?

---

### Card 10
**Front:** Give one strong anti-signal for using sliding window.

---

## Fixed and Variable Windows (10 Cards)

### Card 11
**Front:** In maximum sum subarray of size K, what state is maintained?

---

### Card 12
**Front:** What item leaves the fixed window when index `right` enters?

---

### Card 13
**Front:** Why does fixed-size sliding still work with negative numbers?

---

### Card 14
**Front:** In minimum size subarray sum, why must values be positive?

---

### Card 15
**Front:** When should a minimum-length candidate be recorded?

---

### Card 16
**Front:** When should a maximum-length valid-window candidate be recorded?

---

### Card 17
**Front:** What no-solution value is common for minimum-size subarray sum?

---

### Card 18
**Front:** How do you return boundaries instead of only length or sum?

---

### Card 19
**Front:** Why can each right endpoint trigger multiple left moves?

---

### Card 20
**Front:** What is the common off-by-one bug in variable windows?

---

## Frequency and Counting Windows (10 Cards)

### Card 21
**Front:** What state proves a substring has no repeated characters?

---

### Card 22
**Front:** What must happen when a frequency count drops to zero?

---

### Card 23
**Front:** How do you maintain "at most K distinct" efficiently?

---

### Card 24
**Front:** How do you count subarrays with exactly K distinct values?

---

### Card 25
**Front:** Why does `atMost(K)` add `right-left+1` for each right endpoint?

---

### Card 26
**Front:** What is the main risk when comparing frequency maps every step?

---

### Card 27
**Front:** How does permutation-in-string differ from longest-substring problems?

---

### Card 28
**Front:** What edge case makes permutation-in-string return false immediately?

---

### Card 29
**Front:** How should alphabet size affect your space-complexity statement?

---

### Card 30
**Front:** Name one frequency-window problem that appears in log or event-stream processing.

---

## Deques and System Design Transfer (10 Cards)

### Card 31
**Front:** Why does sliding window maximum need a monotonic deque?

---

### Card 32
**Front:** Why store indices rather than values in the deque?

---

### Card 33
**Front:** What order should values follow inside a max-window deque?

---

### Card 34
**Front:** Why can smaller trailing values be removed from the deque?

---

### Card 35
**Front:** What is the complexity proof for monotonic deque windows?

---

### Card 36
**Front:** How does a sliding-log rate limiter map to array sliding windows?

---

### Card 37
**Front:** Why do production rate limiters often use bucketed sliding counters?

---

### Card 38
**Front:** What extra issue do event-time stream windows introduce?

---

### Card 39
**Front:** What should you monitor for a high-cardinality sliding-window system?

---

### Card 40
**Front:** Give a concise interview wrap-up template for any sliding-window problem.
