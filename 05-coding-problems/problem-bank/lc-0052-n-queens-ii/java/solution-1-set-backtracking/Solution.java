import java.util.HashSet;
import java.util.Set;

class Solution {
    public int totalNQueens(int n) {
        return backtrack(0, n, new HashSet<>(), new HashSet<>(), new HashSet<>());
    }

    private int backtrack(int row, int n, Set<Integer> columns, Set<Integer> diag, Set<Integer> anti) {
        if (row == n) {
            return 1;
        }
        int count = 0;
        for (int col = 0; col < n; col++) {
            int d = row - col;
            int a = row + col;
            if (columns.contains(col) || diag.contains(d) || anti.contains(a)) {
                continue;
            }
            columns.add(col);
            diag.add(d);
            anti.add(a);
            count += backtrack(row + 1, n, columns, diag, anti);
            columns.remove(col);
            diag.remove(d);
            anti.remove(a);
        }
        return count;
    }
}
