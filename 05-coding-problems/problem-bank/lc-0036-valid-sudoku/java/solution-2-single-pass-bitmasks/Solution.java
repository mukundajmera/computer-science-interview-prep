class Solution {
    public boolean isValidSudoku(char[][] board) {
        int[] rows = new int[9];
        int[] cols = new int[9];
        int[] boxes = new int[9];
        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                char value = board[row][col];
                if (value == '.') {
                    continue;
                }
                int bit = 1 << (value - '1');
                int box = (row / 3) * 3 + (col / 3);
                if ((rows[row] & bit) != 0 || (cols[col] & bit) != 0 || (boxes[box] & bit) != 0) {
                    return false;
                }
                rows[row] |= bit;
                cols[col] |= bit;
                boxes[box] |= bit;
            }
        }
        return true;
    }
}
