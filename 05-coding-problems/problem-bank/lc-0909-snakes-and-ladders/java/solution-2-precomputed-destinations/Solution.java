import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public int snakesAndLadders(int[][] board) {
        int n = board.length;
        int total = n * n;
        int[] destination = new int[total + 1];
        for (int square = 1; square <= total; square++) {
            int zero = square - 1;
            int rowFromBottom = zero / n;
            int row = n - 1 - rowFromBottom;
            int col = zero % n;
            if (rowFromBottom % 2 == 1) {
                col = n - 1 - col;
            }
            destination[square] = board[row][col] == -1 ? square : board[row][col];
        }
        boolean[] visited = new boolean[total + 1];
        Queue<Integer> queue = new ArrayDeque<>();
        queue.add(1);
        visited[1] = true;
        int rolls = 0;
        while (!queue.isEmpty()) {
            for (int size = queue.size(); size > 0; size--) {
                int square = queue.remove();
                if (square == total) {
                    return rolls;
                }
                for (int die = 1; die <= 6 && square + die <= total; die++) {
                    int next = destination[square + die];
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
}
