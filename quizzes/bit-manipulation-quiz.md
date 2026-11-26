# Bit Manipulation Quiz

**Difficulty:** Advanced | **Time:** 45 minutes

20 coding-pattern questions for Two's complement, Bitmasks, Kernighan algorithm, Single Number variants, XOR properties.

### Question 1
What does the expression `n & (n - 1)` do?
- **A)** It checks if `n` is odd or even.
- **B)** It clears the lowest (rightmost) set bit of `n`.
- **C)** It isolates the lowest set bit of `n`.
- **D)** It toggles all bits of `n`.

### Question 2
How can you efficiently check if a positive integer `n` is a power of 2?
- **A)** Check if `n % 2 == 0`.
- **B)** Check if `n | (n - 1) == 0`.
- **C)** Check if `(n & (n - 1)) == 0`.
- **D)** Check if `n ^ (n - 1) == 0`.

### Question 3
What does the expression `n & -n` do in a Two's Complement system?
- **A)** It clears the lowest set bit of `n`.
- **B)** It returns the absolute value of `n`.
- **C)** It flips all bits of `n`.
- **D)** It isolates the lowest (rightmost) set bit of `n`.

### Question 4
In the 'Single Number' problem where every element appears twice except for one, what is the optimal solution?
- **A)** Sort the array and scan it linearly.
- **B)** Add all elements and subtract from the expected sum.
- **C)** XOR all the elements together; the result is the single number.
- **D)** Use a Hash Set to track seen numbers.

### Question 5
Why does XORing all elements work for finding the single number in an array of duplicates?
- **A)** Because XOR is commutative and associative, and `a ^ a = 0`, leaving only the unique number `0 ^ x = x`.
- **B)** Because XOR acts as a hash function.
- **C)** Because XOR adds numbers without carrying.
- **D)** Because it isolates the highest set bit.

### Question 6
In 'Single Number II', where every element appears three times except for one, how can bit manipulation solve it?
- **A)** Shift all bits to the right by 3.
- **B)** Count the number of set bits at each position for all numbers; modulo 3 of these counts gives the bits of the unique number.
- **C)** XOR all elements together just like Single Number I.
- **D)** AND all elements together.

### Question 7
In 'Single Number III', where exactly two elements appear once and others twice, what is the first step?
- **A)** XOR all elements to get `a ^ b` (the XOR sum of the two unique numbers).
- **B)** Use `n & (n - 1)` on every element.
- **C)** Find the minimum and maximum elements.
- **D)** Sort the array to group duplicates.

### Question 8
After getting `a ^ b` in Single Number III, how do you separate `a` and `b`?
- **A)** It is mathematically impossible without extra space.
- **B)** Divide the array by the median value.
- **C)** Find any set bit in `a ^ b` (e.g., using `x & -x`) to partition the array into two groups, then XOR each group separately.
- **D)** Modulo the array by `a ^ b`.

### Question 9
What is Brian Kernighan's Algorithm used for?
- **A)** Generating all subsets of a set.
- **B)** Finding the shortest path in a graph.
- **C)** Counting the number of set bits (1s) in an integer efficiently by repeatedly applying `n = n & (n - 1)`.
- **D)** Swapping two variables without a temporary variable.

### Question 10
How do you generate all possible subsets of an array of size N using Bitmasks?
- **A)** Shift the array elements left by N.
- **B)** Use a recursive DFS without any bitwise operators.
- **C)** Iterate from 0 to (2^N - 1); for each number, include array elements where the corresponding bit is 1.
- **D)** Iterate from 0 to N and use a sliding window.

### Question 11
What is the bitwise property `a ^ b ^ a` equal to?
- **A)** b
- **B)** 0
- **C)** -b
- **D)** a

### Question 12
How can you swap two integer variables `x` and `y` without using a temporary variable?
- **A)** x = ~x; y = ~y;
- **B)** x = x ^ y; y = x ^ y; x = x ^ y;
- **C)** x = x & y; y = x & y; x = x & y;
- **D)** x = x | y; y = x | y; x = x | y;

### Question 13
What does the Left Shift operator `x << k` do to a positive integer `x`?
- **A)** Adds `k` to `x`.
- **B)** Inverts `k` bits of `x`.
- **C)** Divides `x` by 2^k.
- **D)** Multiplies `x` by 2^k.

### Question 14
In Two's Complement representation, how is `-x` defined mathematically?
- **A)** `x ^ 1`
- **B)** `~x + 1` (invert all bits and add 1)
- **C)** `~x` (just invert all bits)
- **D)** `x - 1`

### Question 15
If you want to set the i-th bit of an integer `n` to 1, which operation do you use?
- **A)** `n | (1 << i)`
- **B)** `n & (1 << i)`
- **C)** `n ^ (1 << i)`
- **D)** `n & ~(1 << i)`

### Question 16
If you want to check if the i-th bit of an integer `n` is set (is 1), which operation is correct?
- **A)** `(n & (1 << i)) != 0`
- **B)** `(n & ~(1 << i)) == 0`
- **C)** `(n | (1 << i)) == 1`
- **D)** `(n ^ (1 << i)) == 0`

### Question 17
In the 'Missing Number' problem (array containing n distinct numbers in range [0, n]), how does XOR solve it in O(1) space?
- **A)** XOR all array values and check for 0.
- **B)** Apply `n & (n - 1)` to the array sum.
- **C)** Count the set bits of all numbers.
- **D)** XOR all array indices and all array values together; the result is the missing number.

### Question 18
What is the Hamming Distance between two integers `x` and `y`?
- **A)** The absolute difference `|x - y|`.
- **B)** The length of the binary string of `x + y`.
- **C)** The number of bits that are 1 in both `x` and `y`.
- **D)** The number of positions at which the corresponding bits are different, calculated as the set bits in `x ^ y`.

### Question 19
In the problem 'Bitwise AND of Numbers Range' [left, right], what is the optimal strategy?
- **A)** Iterate from `left` to `right` and AND all numbers.
- **B)** Find the common prefix of the binary representations of `left` and `right` by shifting them right until they are equal.
- **C)** Return `left & right`.
- **D)** XOR `left` and `right` and take the complement.

### Question 20
What data structure is highly effective for solving 'Maximum XOR of Two Numbers in an Array' in O(N) time?
- **A)** A Segment Tree.
- **B)** A Min-Heap.
- **C)** A Hash Set storing all possible XOR pairs.
- **D)** A Trie storing the binary representation of each number to aggressively match opposite bits starting from the MSB.
