import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        backtrack(0, n, 0, 0, 0, new int[n], result);
        return result;
    }

    private void backtrack(int row, int n, int cols, int diag, int anti, int[] queens, List<List<String>> result) {
        if (row == n) {
            result.add(render(queens, n));
            return;
        }
        int available = ((1 << n) - 1) & ~(cols | diag | anti);
        while (available != 0) {
            int bit = available & -available;
            available -= bit;
            queens[row] = Integer.numberOfTrailingZeros(bit);
            backtrack(row + 1, n, cols | bit, (diag | bit) << 1, (anti | bit) >> 1, queens, result);
        }
    }

    private List<String> render(int[] queens, int n) {
        List<String> board = new ArrayList<>();
        for (int row = 0; row < n; row++) {
            char[] line = new char[n];
            java.util.Arrays.fill(line, '.');
            line[queens[row]] = 'Q';
            board.add(new String(line));
        }
        return board;
    }
}
