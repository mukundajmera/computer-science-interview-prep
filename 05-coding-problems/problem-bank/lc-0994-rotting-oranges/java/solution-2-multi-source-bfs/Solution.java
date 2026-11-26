import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public int orangesRotting(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        Queue<int[]> queue = new ArrayDeque<>();
        int fresh = 0;
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                if (grid[row][col] == 2) {
                    queue.add(new int[] {row, col});
                } else if (grid[row][col] == 1) {
                    fresh++;
                }
            }
        }
        int minutes = 0;
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (fresh > 0 && !queue.isEmpty()) {
            int layerSize = queue.size();
            for (int i = 0; i < layerSize; i++) {
                int[] current = queue.remove();
                for (int[] direction : directions) {
                    int nextRow = current[0] + direction[0];
                    int nextCol = current[1] + direction[1];
                    if (nextRow < 0 || nextRow >= rows || nextCol < 0 || nextCol >= cols || grid[nextRow][nextCol] != 1) {
                        continue;
                    }
                    grid[nextRow][nextCol] = 2;
                    fresh--;
                    queue.add(new int[] {nextRow, nextCol});
                }
            }
            minutes++;
        }
        return fresh == 0 ? minutes : -1;
    }
}
