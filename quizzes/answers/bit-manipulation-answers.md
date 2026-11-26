# Bit Manipulation Quiz - Answers

1. **B**

**Explanation:**
(Assumption: `n` is a non-zero integer within standard machine limits.) Subtracting 1 from `n` flips all bits up to and including the lowest set bit. ANDing this result with the original `n` clears that specific bit while leaving higher bits intact. Option C describes `n & -n`. Options A and D are incorrect.

2. **C**

**Explanation:**
A power of 2 (e.g., 4, 8, 16) has exactly one bit set in binary (e.g., 100, 1000). Applying `n & (n - 1)` clears this single bit, resulting in 0. Option A only checks if it's even. The other bitwise operations do not satisfy this invariant.

3. **D**

**Explanation:**
(Assumption: Standard 32-bit or 64-bit integer constraints apply where negative numbers are represented via Two's Complement.) In Two's complement, `-n` is equivalent to `~n + 1`. This mathematical property flips all bits to the left of the lowest set bit, but preserves the lowest set bit as a 1. Thus, `n & -n` extracts exclusively that bit (e.g., 12 & -12 = 4).

4. **C**

**Explanation:**
XOR is associative, commutative, and has the property `x ^ x = 0`. XORing all numbers annihilates all duplicates, leaving only the single unique number in O(N) time and O(1) space. The other options require O(N) space or O(N log N) time.

5. **A**

**Explanation:**
The mathematical properties of XOR allow order to be ignored (commutativity) and grouped (associativity). Duplicates cancel out to 0, and 0 XOR the unique number yields the unique number. The other statements are factually incorrect.

6. **B**

**Explanation:**
Because elements appear three times, the sum of bits at any given position `i` across all numbers will be a multiple of 3. Any remainder (1) after modulo 3 must belong to the single unique number. XOR fails because `x ^ x ^ x = x`, not 0.

7. **A**

**Explanation:**
By XORing all elements, the duplicates cancel out, leaving the XOR sum of the two unique targets, `a ^ b`. This is the mandatory first step before partitioning. Sorting takes O(N log N), failing the typical optimal O(N) requirement.

8. **C**

**Explanation:**
Because `a` and `b` are different, `a ^ b` must have at least one set bit. By isolating this bit (e.g., `(a^b) & -(a^b)`), we can split the original array into two groups: those with this bit set, and those without. `a` goes to one, `b` to the other, isolating them.

9. **C**

**Explanation:**
By applying `n & (n - 1)`, we strip away the lowest set bit. Repeating this until the number becomes 0 allows us to count set bits in O(k) iterations, where k is the number of set bits, avoiding iterating through all 32 bits. The other descriptions are unrelated.

10. **C**

**Explanation:**
There are 2^N possible subsets. By counting from 0 to 2^N - 1, the binary representation of each integer uniquely maps to a combination of included (bit=1) and excluded (bit=0) elements, effectively generating the power set. The other options are incorrect.

11. **A**

**Explanation:**
Due to commutativity and associativity, `a ^ b ^ a` is equivalent to `(a ^ a) ^ b`. Since a number XORed with itself is 0, this evaluates to `0 ^ b`, which is exactly `b`. The distractors fundamentally misunderstand XOR.

12. **B**

**Explanation:**
This classic trick uses XOR logic. Step 1: `x` becomes `x^y`. Step 2: `y` becomes `(x^y)^y = x`. Step 3: `x` becomes `(x^y)^x = y`. The variables are perfectly swapped. The other logical operators destroy the original state data.

13. **D**

**Explanation:**
Shifting binary digits to the left by `k` positions is mathematically equivalent to multiplying the base-10 value by 2 raised to the power of `k`. Option C describes the Right Shift `>>` operator. Addition and Inversion are incorrect.

14. **B**

**Explanation:**
(Assumption: Modern architectures use Two's Complement for signed integers, meaning fixed bit-width overflow wraps seamlessly.) Modern CPUs use Two's Complement for negative numbers because it handles zero optimally and simplifies arithmetic circuits. The conversion involves a bitwise NOT (`~x`) followed by adding 1. Option C is One's Complement, an older standard.

15. **A**

**Explanation:**
By shifting a `1` left by `i` positions, we create a mask (e.g., 00100). Performing a bitwise OR with `n` ensures that the i-th bit becomes 1, regardless of its previous state, while leaving other bits unchanged. Option B isolates it. Option C toggles it. Option D clears it.

16. **A**

**Explanation:**
Creating a mask with a 1 at the i-th position and ANDing it with `n` will isolate that bit. If the result is not zero, it means the bit was originally 1 in `n`. The other options use incorrect operators or comparison values for this check.

17. **D**

**Explanation:**
By XORing the numbers `0` through `n` alongside the actual array values, every present number appears twice (once as an index/target, once in the array) and cancels out to 0. The missing number appears only once, thus remaining as the final result.

18. **D**

**Explanation:**
XORing `x` and `y` yields a 1 in every bit position where the two numbers differ. Therefore, the Hamming Distance is simply the count of set bits (Hamming weight) of the result of `x ^ y`. The distractors describe mathematical magnitude, not bitwise distance.

19. **B**

**Explanation:**
(Assumption: We operate within standard bounds like a 32-bit signed integer space where `left <= right`.) Because of the contiguous range, any bit position that changes between `left` and `right` will inevitably contain a 0 somewhere in the sequence, zeroing out that bit in the final AND result. The only bits that survive are the identical prefix bits. Option A hits Time Limit Exceeded (TLE).

20. **D**

**Explanation:**
To maximize XOR, we need to find pairs with opposing bits, prioritizing the most significant bits (MSB) first. Inserting all binary strings into a Trie allows us to greedily traverse the opposite path for each number, yielding optimal pairs in linear time. The other structures lack bitwise routing.
