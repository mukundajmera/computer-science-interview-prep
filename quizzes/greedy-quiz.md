# Greedy Quiz

> 32 multiple-choice questions plus written proof drills to test greedy recognition, proof style, interval choices, reachability, boundary resets, counterexamples, and system-design transfer.
>
> Time: 40 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
What makes a greedy algorithm correct?

A) A proof that the local choice is globally safe
B) The code is shorter than DP
C) The input is always sorted
D) The answer uses no extra memory

### Question 2
Which proof shape is common for interval scheduling?

A) Hash collision proof
B) Heap-order proof
C) Exchange argument
D) Recursion-depth proof

### Question 3
Which prompt most strongly suggests earliest-finish greedy?

A) Count all valid subsets
B) Select maximum non-overlapping activities
C) Find longest common subsequence
D) Clone a graph

### Question 4
Which prompt should make you suspicious of greedy?

A) Minimum arrows for intervals
B) Can reach the end with jumps
C) Best one-transaction stock profit
D) Arbitrary coin change with largest coin first

### Question 5
What is the strongest recognition cue for Jump Game?

A) Need all permutations
B) Farthest reachable boundary
C) Prefix trie lookup
D) Weighted shortest path

### Question 6
Which problem uses a reset after a negative running balance?

A) Partition Labels
B) Activity Selection
C) Gas Station
D) Minimum Arrows

### Question 7
Which problem uses last occurrence as a boundary?

A) Non-overlapping Intervals
B) Best Time to Buy and Sell Stock
C) Activity Selection
D) Partition Labels

### Question 8
Which system-design use is an exact greedy analogy only if you can prove the local choice is safe?

A) Scheduling by earliest finish or deadline
B) Rendering Markdown
C) Renaming a route
D) Reading a config file

## Section 2: Invariants and Proofs

### Question 9
In Activity Selection, why sort by end time?

A) It sorts by shortest duration
B) It leaves the most remaining room for future intervals
C) It avoids all ties
D) It removes the need to scan

### Question 10
In Non-overlapping Intervals, minimum removals is equivalent to:

A) choosing the longest interval first
B) sorting by start time only
C) merging every interval
D) keeping the maximum number of compatible intervals

### Question 11
In Jump Game, what does `farthest` represent?

A) The maximum index reachable after scanning reachable positions
B) The shortest path length
C) The number of jumps used
D) The last unreachable index

### Question 12
When should Jump Game return false?

A) When any value is zero
B) When the array length is odd
C) When the scan reaches an index beyond `farthest`
D) When `farthest` changes

### Question 13
In Gas Station, why can starts inside a failed segment be skipped?

A) They are sorted by station id
B) They have larger tank capacity
C) The route is not circular
D) They inherit an even worse balance before the failure point

### Question 14
What must be checked before returning a Gas Station start?

A) Every station has positive gas
B) Total gas minus total cost is non-negative
C) Costs are sorted
D) The first station is profitable

### Question 15
In Partition Labels, when can a segment close?

A) At the first repeated character
B) After sorting the string
C) When the current index reaches the maximum last occurrence of characters in the segment
D) At every vowel

### Question 16
For one-transaction stock profit, what is the dominant state?

A) Lowest previous buy price
B) Highest future sell price known in advance
C) Median price
D) Number of transactions remaining

## Section 3: Complexity and Edge Cases

### Question 17
Activity Selection time complexity is usually:

A) `O(1)`
B) `O(n log n)` because of sorting plus a linear scan
C) `O(2^n)`
D) `O(n^3)`

### Question 18
Which endpoint condition matters in Minimum Arrows for inclusive intervals?

A) `start >= arrow_pos` means covered
B) Every balloon needs a new arrow
C) Sort by midpoint only
D) A new arrow is needed only when `start > arrow_pos`

### Question 19
What is a common greedy mistake?

A) Providing an exchange proof
B) Handling empty input
C) Sorting by a convenient key without proving it
D) Separating exact algorithms from heuristics

### Question 20
What should stock profit return for decreasing prices?

A) `0`
B) The smallest loss
C) The last price
D) `-1`

### Question 21
Why is arbitrary coin change not a safe greedy default?

A) Coins are numeric
B) Sorting is impossible
C) There is no objective
D) Largest-coin choice can be suboptimal

### Question 22
What is the space complexity of Jump Game reachability?

A) `O(n)` mandatory
B) `O(1)` extra space
C) `O(n^2)`
D) recursion stack only

### Question 23
Which tie case should be clarified for interval problems?

A) Whether `end == start` counts as overlap
B) Whether strings are Unicode
C) Whether a graph is directed
D) Whether prices are floats

### Question 24
What is the safest way to present a production greedy policy without exact proof?

A) Claim it is optimal
B) Hide failures
C) Call it a heuristic and add observability, guardrails, and rollback
D) Remove metrics

## Section 4: System Design Transfer

### Question 25
How does greedy map to cache eviction?

A) It always proves optimality
B) Eviction uses a local victim choice that needs metrics and workload fit
C) It replaces consistency checks
D) It eliminates hot keys

### Question 26
How does earliest-finish reasoning map to schedulers?

A) Pick arbitrary jobs
B) Ignore deadlines
C) Always use recursion
D) Choose jobs that preserve future scheduling flexibility

### Question 27
What is the production equivalent of a weak greedy proof?

A) A heuristic policy that needs monitoring and rollback
B) A strongly consistent transaction
C) A static asset route
D) A complete correctness guarantee

### Question 28
Which validation signal fits a greedy load-assignment heuristic?

A) Number of Markdown files
B) CSS bundle size only
C) skew, p95 latency, rejection rate, and rollback events
D) Number of class names

### Question 29
Why should a candidate mention counterexamples?

A) To avoid explaining the algorithm
B) To make the answer longer
C) To skip complexity
D) To show they know when greedy is unsafe

### Question 30
Which phrase is strongest in a greedy wrap-up?

A) "I can prove this local choice is safe by an exchange or boundary argument."
B) "Greedy is always faster."
C) "Sorting means it is correct."
D) "I will try it and see."

### Question 31
What should you say when a greedy solution fails on a variant?

A) Ignore the variant
B) Claim constraints prevent all failures without checking
C) Switch to DP, heap, graph search, or another model based on the new dependency
D) Keep the same code

### Question 32
Which production use best matches Partition Labels?

A) Weighted shortest path
B) Creating isolated batches where keys cannot cross batch boundaries
C) Full-text relevance ranking
D) CPU instruction scheduling only

## Written Proof Drills

### Proof Drill A
Give the exchange argument for sorting activities by earliest finish time.

### Proof Drill B
Explain why Jump Game reachability can ignore every path except the farthest reachable boundary.

### Proof Drill C
For Gas Station, prove why a negative running balance invalidates every start inside the failed segment.

### Proof Drill D
For Minimum Arrows, prove why shooting at the earliest end of the first uncovered interval is safe.

### Proof Drill E
Give one counterexample where a tempting greedy rule fails and name the correct pattern.

### Proof Drill F
Explain how you would present a production greedy policy when exact optimality is not proven.
