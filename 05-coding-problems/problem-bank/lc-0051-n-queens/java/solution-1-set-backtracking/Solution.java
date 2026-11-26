import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        int[] queens = new int[n];
        backtrack(0, n, queens, new HashSet<>(), new HashSet<>(), new HashSet<>(), result);
        return result;
    }

    private void backtrack(int row, int n, int[] queens, Set<Integer> cols, Set<Integer> diag, Set<Integer> anti, List<List<String>> result) {
        if (row == n) {
            result.add(render(queens, n));
            return;
        }
        for (int col = 0; col < n; col++) {
            if (cols.contains(col) || diag.contains(row - col) || anti.contains(row + col)) {
                continue;
            }
            queens[row] = col;
            cols.add(col);
            diag.add(row - col);
            anti.add(row + col);
            backtrack(row + 1, n, queens, cols, diag, anti, result);
            cols.remove(col);
            diag.remove(row - col);
            anti.remove(row + col);
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
