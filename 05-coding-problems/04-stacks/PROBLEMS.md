# 🧩 Stacks Problems

1. **Valid Parentheses**

   - *Summary*: Decide whether a string of brackets is correctly matched and nested.
   - *Practice*: [lc-0020-valid-parentheses](../problem-bank/lc-0020-valid-parentheses/README.md)

   - *Hints*: 1. Use a hash map for matching. 2. Push open brackets. 3. Pop on close brackets.
   - *Complexity*: Time O(N), Space O(N)

2. **Min Stack**

   - *Summary*: Design a stack that also returns its minimum value in constant time.
   - *Practice*: [lc-0155-min-stack](../problem-bank/lc-0155-min-stack/README.md)

   - *Hints*: 1. Use two stacks. 2. Second stack tracks minimums. 3. Push to min stack if value <= current min.
   - *Complexity*: Time O(1), Space O(N)

3. **Evaluate Reverse Polish Notation**

   - *Summary*: Compute the value of an arithmetic expression written in postfix form.
   - *Practice*: [lc-0150-evaluate-reverse-polish-notation](../problem-bank/lc-0150-evaluate-reverse-polish-notation/README.md)

   - *Hints*: 1. Push numbers. 2. On operator, pop two and compute. 3. Division truncates toward zero.
   - *Complexity*: Time O(N), Space O(N)

4. **Generate Parentheses**

   - *Summary*: List every balanced arrangement of n pairs of parentheses.
   - *Practice*: [lc-0022-generate-parentheses](../problem-bank/lc-0022-generate-parentheses/README.md)

   - *Hints*: 1. Backtracking. 2. Add '(' if open < n. 3. Add ')' if closed < open.
   - *Complexity*: Time O(4^N / sqrt(N)), Space O(N)

5. **Daily Temperatures**

   - *Summary*: For each day, count how many days pass until a warmer temperature appears.
   - *Practice*: [lc-0739-daily-temperatures](../problem-bank/lc-0739-daily-temperatures/README.md)

   - *Hints*: 1. Monotonic decreasing stack. 2. Store indices. 3. Pop when finding warmer day.
   - *Complexity*: Time O(N), Space O(N)

6. **Car Fleet**

   - *Summary*: Cars drive toward one destination and cannot pass each other; count how many separate groups arrive.

   - *Hints*: 1. Sort by position descending. 2. Calculate arrival times. 3. Monotonic stack for fleets.
   - *Complexity*: Time O(N log N), Space O(N)

7. **Largest Rectangle in Histogram**

   - *Summary*: Given bar heights, find the largest rectangle that fits entirely under the bars.
   - *Practice*: [lc-0084-largest-rectangle-in-histogram](../problem-bank/lc-0084-largest-rectangle-in-histogram/README.md)

   - *Hints*: 1. Monotonic increasing stack. 2. Store (index, height). 3. Pop when height decreases, calculate area.
   - *Complexity*: Time O(N), Space O(N)
