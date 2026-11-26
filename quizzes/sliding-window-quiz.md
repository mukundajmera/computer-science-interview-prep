# 🪟 Sliding Window Quiz

> **32 questions to test your sliding-window recognition, invariants, state maintenance, and system-design transfer**
>
> ⏱️ Time: 40 minutes | ⭐⭐⭐ Difficulty

---

## Section 1: Pattern Recognition (8 questions)

### Question 1 ⭐
Which problem signal most strongly suggests sliding window?

**A)** Non-contiguous subsequence choices  
**B)** Graph reachability  
**C)** Contiguous substring with a maintained validity condition  
**D)** Arbitrary pair selection after reordering  

---

### Question 2 ⭐
Fixed-size sliding window is the best first choice when the prompt says:

**A)** choose any `k` elements  
**B)** exactly `k` consecutive elements  
**C)** sort by frequency  
**D)** find shortest path  

---

### Question 3 ⭐⭐
For variable-size windows, the key predicate usually tells you:

**A)** whether recursion should stop  
**B)** which graph node to visit next  
**C)** whether the current window is valid or must shrink  
**D)** which item to sort first  

---

### Question 4 ⭐⭐
Which case can break the basic positive-sum shrink-while-valid template?

**A)** `k = 1`  
**B)** input is contiguous  
**C)** all values are positive  
**D)** negative numbers are allowed  

---

### Question 5 ⭐⭐
Which problem often uses `atMost(K) - atMost(K - 1)`?

**A)** topological sort  
**B)** subarrays with exactly K distinct values  
**C)** binary search lower bound  
**D)** maximum of every window  

---

### Question 6 ⭐⭐
Permutation-in-string is primarily:

**A)** heap scheduling  
**B)** graph coloring  
**C)** dynamic programming  
**D)** fixed-size frequency-window matching  

---

### Question 7 ⭐⭐⭐
Sliding window maximum needs which extra data structure for `O(n)` time?

**A)** stack of all values  
**B)** union-find  
**C)** monotonic deque of candidate indices  
**D)** sorted array rebuilt each step  

---

### Question 8 ⭐⭐⭐
Which production system is most directly related to sliding-window reasoning?

**A)** leader election  
**B)** relational schema normalization  
**C)** API rate limiter over the last 60 seconds  
**D)** class factory selection  

---

## Section 2: Invariants and State (10 questions)

### Question 9 ⭐
In a fixed-size sum window, when a new right item enters, what else must happen after the first full window?

**A)** reset the sum  
**B)** sort the full array  
**C)** move right backward  
**D)** remove the outgoing left item  

---

### Question 10 ⭐
For an inclusive window `[left, right]`, window length is:

**A)** `right - left + 1`  
**B)** `left - right + 1`  
**C)** `right + left`  
**D)** `right - left`  

---

### Question 11 ⭐⭐
In longest substring without repeating characters, the window is valid when:

**A)** every character count is at most one  
**B)** the string is sorted  
**C)** all characters are lowercase  
**D)** left equals right  

---

### Question 12 ⭐⭐
When a frequency-map count drops to zero during shrink, why remove the key?

**A)** to reduce time from linear to constant  
**B)** to keep distinct-count logic accurate  
**C)** to preserve sorted order  
**D)** to avoid recursion  

---

### Question 13 ⭐⭐
For longest substring with at most K distinct characters, when should `best` be updated?

**A)** after the shrink loop restores validity  
**B)** before adding the right item  
**C)** only while the window is invalid  
**D)** after sorting the map keys  

---

### Question 14 ⭐⭐
For minimum-size subarray sum with positive integers, when should the candidate length be recorded?

**A)** only after all right indices finish  
**B)** before the window reaches target  
**C)** inside the loop while `window_sum >= target`, before removing left  
**D)** never; use binary search only  

---

### Question 15 ⭐⭐⭐
In `atMost(K)` counting, why add `right - left + 1` after restoring validity?

**A)** every start from `left` to `right` forms a valid subarray ending at `right`  
**B)** it counts only one window  
**C)** it is the number of distinct values  
**D)** it is always equal to `K`  

---

### Question 16 ⭐⭐⭐
In sliding window maximum, why store indices instead of values in the deque?

**A)** indices let you expire entries that leave the window  
**B)** values cannot be compared  
**C)** values require recursion  
**D)** indices are always smaller  

---

### Question 17 ⭐⭐⭐
The monotonic deque for sliding maximum keeps values in which order from front to back?

**A)** sorted by original frequency  
**B)** increasing  
**C)** decreasing  
**D)** random  

---

### Question 18 ⭐⭐⭐
What proof gives most sliding-window solutions linear time?

**A)** nested loops always become linear  
**B)** each item enters and leaves the window at most once  
**C)** hash maps are free  
**D)** each boundary moves backward often  

---

## Section 3: Complexity and Edge Cases (8 questions)

### Question 19 ⭐
Maximum sum subarray of size K target complexity:

**A)** `O(nk)` time, `O(1)` space  
**B)** `O(n)` time, `O(1)` space  
**C)** `O(n^2)` time  
**D)** `O(log n)` time  

---

### Question 20 ⭐
Longest substring without repeating characters usually uses space:

**A)** `O(log n)`  
**B)** `O(n^2)`  
**C)** `O(alphabet)` or `O(distinct active chars)`  
**D)** `O(1)` always, regardless of alphabet  

---

### Question 21 ⭐⭐
If `k = 0` in "at most K distinct characters", the longest valid length is:

**A)** the full string  
**B)** undefined for all inputs  
**C)** 0  
**D)** 1  

---

### Question 22 ⭐⭐
Permutation-in-string can immediately return false when:

**A)** `s1` has duplicates  
**B)** `len(s1) > len(s2)`  
**C)** `s2` is lowercase  
**D)** both strings are non-empty  

---

### Question 23 ⭐⭐
Sliding window maximum target complexity with deque:

**A)** `O(n log n)` time, `O(n)` space  
**B)** `O(n)` time, `O(k)` space  
**C)** `O(nk)` time, `O(1)` space  
**D)** `O(k)` time total  

---

### Question 24 ⭐⭐
Which edge case should fixed-window problems handle explicitly?

**A)** invalid class inheritance  
**B)** graph cycles  
**C)** leader failover  
**D)** `k = n`  

---

### Question 25 ⭐⭐⭐
Which answer is safest for sum windows when negatives are allowed?

**A)** sort the input first  
**B)** check if monotonicity still holds; often switch to prefix sums or deque techniques  
**C)** always use the same shrink-while-sum-too-large template  
**D)** ignore negatives  

---

### Question 26 ⭐⭐⭐
For very large alphabets, frequency-window space should be described as:

**A)** proportional to active distinct symbols or required target symbols  
**B)** equal to the number of windows  
**C)** impossible to analyze  
**D)** always `O(1)`  

---

## Section 4: System Design Adjacency (6 questions)

### Question 27 ⭐⭐
A sliding-log rate limiter stores:

**A)** every request forever only  
**B)** graph edges  
**C)** sorted user names  
**D)** timestamps of recent requests inside the active window  

---

### Question 28 ⭐⭐
Why do production sliding counters often use buckets?

**A)** buckets make time stop  
**B)** exact per-event logs are always cheaper  
**C)** buckets remove need for clocks  
**D)** buckets trade exactness for lower memory and simpler cleanup  

---

### Question 29 ⭐⭐⭐
Event-time stream windows need extra care for:

**A)** late-arriving events  
**B)** constructor overloading  
**C)** CSS layout  
**D)** binary tree rotations  

---

### Question 30 ⭐⭐⭐
Rolling maximum over a metric stream is closest to which interview problem?

**A)** LRU cache eviction only  
**B)** 3-sum  
**C)** N-Queens  
**D)** sliding window maximum  

---

### Question 31 ⭐⭐⭐
Which metric should you monitor for a production sliding-window limiter?

**A)** active window memory per key  
**B)** branch naming style  
**C)** source file line count only  
**D)** number of Java classes  

---

### Question 32 ⭐⭐⭐
What is the best interview wrap-up for sliding window?

**A)** "I used a loop and it passed samples."  
**B)** "Sliding window works for every array problem."  
**C)** "This is always constant space."  
**D)** "The maintained state is X, validity is Y, each boundary moves at most n times, so time is O(n)."  

---

