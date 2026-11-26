# 16-matrices Problems

## Valid Sudoku

**Summary:** Check that the filled cells of a partially completed 9-by-9 Sudoku board break no row, column, or box rule.
**Practice:** [lc-0036-valid-sudoku](problem-bank/lc-0036-valid-sudoku/README.md)

**Hints:** 
1. Use hash sets to keep track of the values seen in each row, column, and 3x3 box.
2. You can map each cell `(r, c)` to a specific 3x3 box index using `(r // 3) * 3 + (c // 3)`.
3. Iterate through each cell, and if it is not empty, check if its value exists in the corresponding row, column, or box set.
**Complexity:** O(1) time (since the board is always 9x9), O(1) space

## Spiral Matrix

**Summary:** Return the elements of a matrix in clockwise spiral order.
**Practice:** [lc-0054-spiral-matrix](problem-bank/lc-0054-spiral-matrix/README.md)

**Hints:** 
1. Maintain 4 pointers: top, bottom, left, and right to define the current boundaries.
2. Traverse the top row from left to right, then increment top.
3. Traverse the right column from top to bottom, then decrement right. Continue similarly for bottom and left, making sure boundaries don't cross.
**Complexity:** O(m * n) time, O(1) extra space

## Rotate Image

**Summary:** Rotate a square matrix ninety degrees clockwise in place.
**Practice:** [lc-0048-rotate-image](problem-bank/lc-0048-rotate-image/README.md)

**Hints:** 
1. A clockwise rotation by 90 degrees can be achieved by first transposing the matrix, then reversing each row.
2. Alternatively, rotate layer by layer from outside in, swapping 4 cells at a time.
3. Keep track of the four corners (top-left, top-right, bottom-right, bottom-left) and shift them simultaneously.
**Complexity:** O(n^2) time, O(1) space

## Set Matrix Zeroes

**Summary:** If a matrix cell is zero, set its entire row and column to zero, ideally without extra space.
**Practice:** [lc-0073-set-matrix-zeroes](problem-bank/lc-0073-set-matrix-zeroes/README.md)

**Hints:** 
1. To do this in O(1) space, use the first row and first column of the matrix to keep track of which rows and columns need to be set to zero.
2. Since the first element `matrix[0][0]` overlaps for the first row and column, use an extra variable (like `rowZero`) to track if the first row needs to be zeroed.
3. After marking, iterate from `r = 1` and `c = 1` to fill the zeroes. Finally, handle the first row and first column based on your tracking variables.
**Complexity:** O(m * n) time, O(1) space

## Game of Life

**Summary:** Advance a grid of live and dead cells by one generation using neighbour-count rules, updating in place.
**Practice:** [lc-0289-game-of-life](problem-bank/lc-0289-game-of-life/README.md)

**Hints:** 
1. To do this in-place, encode the next state into the current value so you can retrieve both the current and next state.
2. For example, if a cell goes from 0 -> 1, mark it as 2. If it goes from 1 -> 0, mark it as 3.
3. When counting live neighbors, check if the value is 1 or 3 (meaning it was originally 1). Finally, replace all 2s with 1s and 3s with 0s.
**Complexity:** O(m * n) time, O(1) space

## Search a 2D Matrix

**Summary:** Search for a value in a matrix whose rows are sorted and each row continues from the previous one.
**Practice:** [lc-0074-search-a-2d-matrix](problem-bank/lc-0074-search-a-2d-matrix/README.md)

**Hints:** 
1. Because of the sorting properties, if we flatten the matrix it becomes a single sorted array.
2. We can use binary search twice: first to find the correct row, then to find the correct element in that row.
3. Alternatively, treat the 2D matrix as a 1D array of length `m * n` and do a single binary search. The index `i` maps to `matrix[i // n][i % n]`.
**Complexity:** O(log(m * n)) time, O(1) space

