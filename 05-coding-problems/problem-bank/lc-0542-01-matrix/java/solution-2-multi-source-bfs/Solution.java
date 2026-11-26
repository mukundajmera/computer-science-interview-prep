import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Queue;

class Solution {
    public int[][] updateMatrix(int[][] mat) {
        int rows = mat.length;
        int cols = mat[0].length;
        int[][] distance = new int[rows][cols];
        Queue<int[]> queue = new ArrayDeque<>();
        for (int row = 0; row < rows; row++) {
            Arrays.fill(distance[row], -1);
            for (int col = 0; col < cols; col++) {
                if (mat[row][col] == 0) {
                    distance[row][col] = 0;
                    queue.add(new int[] {row, col});
                }
            }
        }
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!queue.isEmpty()) {
            int[] current = queue.remove();
            for (int[] direction : directions) {
                int nextRow = current[0] + direction[0];
                int nextCol = current[1] + direction[1];
                if (nextRow < 0 || nextRow >= rows || nextCol < 0 || nextCol >= cols || distance[nextRow][nextCol] != -1) {
                    continue;
                }
                distance[nextRow][nextCol] = distance[current[0]][current[1]] + 1;
                queue.add(new int[] {nextRow, nextCol});
            }
        }
        return distance;
    }
}
