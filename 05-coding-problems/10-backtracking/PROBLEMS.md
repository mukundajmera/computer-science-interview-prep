# Backtracking Problems

## 1. Subsets

**Summary:** List every possible subset of a set of distinct numbers.
**Practice:** [lc-0078-subsets](problem-bank/lc-0078-subsets/README.md)

**Hints**:
1. At each element, you have two choices: include it or exclude it.
2. Maintain a `path` list and index `i`. 
3. Recurse for `i+1` both with and without `nums[i]`.
**Complexity**: O(N * 2^N) Time, O(N) Space

## 2. Combination Sum

**Summary:** List every unique combination of candidate numbers (each reusable) that sums to a target.
**Practice:** [lc-0039-combination-sum](problem-bank/lc-0039-combination-sum/README.md)

**Hints**:
1. Sort candidates to prune early if sum exceeds target.
2. Since you can reuse elements, when you recurse after choosing `candidates[i]`, pass `i` again, not `i+1`.
3. If sum equals target, add path to result. If sum > target, return.
**Complexity**: O(N^(T/M + 1)) Time where T is target, M is min value. Space O(T/M).

## 3. Combinations

**Summary:** Generate every way to choose k numbers out of 1 through n.
**Practice:** [lc-0077-combinations](problem-bank/lc-0077-combinations/README.md)

**Hints**:
1. Start backtracking with `start = 1`.
2. Iterate `i` from `start` to `n`. Add `i` to path, recurse with `i+1`, remove `i`.
3. Stop when path length is `k`.
**Complexity**: O(k * C(n,k)) Time, O(k) Space

## 4. Permutations

**Summary:** List every ordering of a set of distinct numbers.
**Practice:** [lc-0046-permutations](problem-bank/lc-0046-permutations/README.md)

**Hints**:
1. Use a boolean array to track used elements, or just check if `num` is in `path`.
2. Iterate through all `nums`. If not used, choose, explore, unchoose.
3. Base case: `len(path) == len(nums)`.
**Complexity**: O(N * N!) Time, O(N) Space

## 5. Generate Parentheses

**Summary:** List every balanced arrangement of n pairs of parentheses.
**Practice:** [lc-0022-generate-parentheses](problem-bank/lc-0022-generate-parentheses/README.md)

**Hints**:
1. Keep track of the number of opening and closing brackets placed.
2. You can place an opening bracket if `open_count < n`.
3. You can place a closing bracket if `close_count < open_count`.
**Complexity**: O(4^n / sqrt(n)) Time and Space (Catalan number).

## 6. Word Search

**Summary:** Decide whether a word can be traced through adjacent cells of a letter grid without reusing a cell.
**Practice:** [lc-0079-word-search](problem-bank/lc-0079-word-search/README.md)

**Hints**:
1. Search starting from each cell matching `word[0]`.
2. Use DFS to explore 4 directions.
3. Mark visited cells (e.g., by changing character temporarily to `#`) to avoid reuse.
**Complexity**: O(m * n * 4^L) Time where L is word length, O(L) Space.

## 7. N-Queens

**Summary:** Place n queens on an n-by-n board so that none attack each other, and list the valid layouts.
**Practice:** [lc-0051-n-queens](problem-bank/lc-0051-n-queens/README.md)

**Hints**:
1. Place queens row by row.
2. Maintain sets for columns, positive diagonals (`r+c`), and negative diagonals (`r-c`) to check attacks in O(1).
3. If row == n, valid board found.
**Complexity**: O(N!) Time, O(N) Space.

## 8. Letter Combinations of a Phone Number

**Summary:** Given digits on a phone keypad, list every letter string they could spell.
**Practice:** [lc-0017-letter-combinations-of-a-phone-number](problem-bank/lc-0017-letter-combinations-of-a-phone-number/README.md)

**Hints**:
1. Map digits to letters (e.g., `'2': 'abc'`).
2. Iterate through letters for the current digit, append to path, recurse for next digit.
3. Base case: index equals `digits.length`.
**Complexity**: O(4^N * N) Time, O(N) Space where N is digits length.
