class Solution {
    public int totalNQueens(int n) {
        int mask = (1 << n) - 1;
        return backtrack(mask, 0, 0, 0);
    }

    private int backtrack(int mask, int columns, int diag, int anti) {
        if (columns == mask) {
            return 1;
        }
        int count = 0;
        int available = mask & ~(columns | diag | anti);
        while (available != 0) {
            int bit = available & -available;
            available -= bit;
            count += backtrack(mask, columns | bit, (diag | bit) << 1, (anti | bit) >> 1);
        }
        return count;
    }
}
