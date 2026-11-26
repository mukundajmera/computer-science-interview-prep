import java.util.ArrayList;
import java.util.List;

class Solution {
    public void solveSudoku(char[][] board) {
        int[] rows = new int[9];
        int[] cols = new int[9];
        int[] boxes = new int[9];
        List<int[]> blanks = new ArrayList<>();
        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board[row][col] == '.') {
                    blanks.add(new int[] {row, col});
                } else {
                    int bit = 1 << (board[row][col] - '1');
                    rows[row] |= bit;
                    cols[col] |= bit;
                    boxes[box(row, col)] |= bit;
                }
            }
        }
        solve(board, 0, blanks, rows, cols, boxes);
    }

    private boolean solve(char[][] board, int index, List<int[]> blanks, int[] rows, int[] cols, int[] boxes) {
        if (index == blanks.size()) {
            return true;
        }
        int row = blanks.get(index)[0];
        int col = blanks.get(index)[1];
        int box = box(row, col);
        int used = rows[row] | cols[col] | boxes[box];
        for (int digit = 0; digit < 9; digit++) {
            int bit = 1 << digit;
            if ((used & bit) != 0) {
                continue;
            }
            rows[row] |= bit;
            cols[col] |= bit;
            boxes[box] |= bit;
            board[row][col] = (char) ('1' + digit);
            if (solve(board, index + 1, blanks, rows, cols, boxes)) {
                return true;
            }
            rows[row] ^= bit;
            cols[col] ^= bit;
            boxes[box] ^= bit;
            board[row][col] = '.';
        }
        return false;
    }

    private int box(int row, int col) {
        return (row / 3) * 3 + col / 3;
    }
}
