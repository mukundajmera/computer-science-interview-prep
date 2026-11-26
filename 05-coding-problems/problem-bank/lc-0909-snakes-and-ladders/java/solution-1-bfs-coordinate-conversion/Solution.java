import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public int snakesAndLadders(int[][] board) {
        int n = board.length;
        boolean[] visited = new boolean[n * n + 1];
        Queue<Integer> queue = new ArrayDeque<>();
        queue.add(1);
        visited[1] = true;
        int rolls = 0;
        while (!queue.isEmpty()) {
            for (int size = queue.size(); size > 0; size--) {
                int square = queue.remove();
                if (square == n * n) {
                    return rolls;
                }
                for (int die = 1; die <= 6 && square + die <= n * n; die++) {
                    int next = square + die;
                    int[] rc = coordinates(next, n);
                    if (board[rc[0]][rc[1]] != -1) {
                        next = board[rc[0]][rc[1]];
                    }
                    if (!visited[next]) {
                        visited[next] = true;
                        queue.add(next);
                    }
                }
            }
            rolls++;
        }
        return -1;
    }

    private int[] coordinates(int square, int n) {
        int zero = square - 1;
        int rowFromBottom = zero / n;
        int row = n - 1 - rowFromBottom;
        int col = zero % n;
        if (rowFromBottom % 2 == 1) {
            col = n - 1 - col;
        }
        return new int[] {row, col};
    }
}
